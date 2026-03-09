const crypto = require('crypto');
const express = require('express');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const db = require('./db');
const path = require('path');
const { browse } = require('./bot');

const app = express();
const PORT = 6969;
const JWT_SECRET = process.env.JWT_SECRET || "dev_secret";
const GAME_SEED = process.env.GAME_SEED || "CASINO_SHNENANIGANS";
const FLAG = process.env.FLAG || "upCTF{juro_que_esta_flag_é_verdadeira}";
const TARGET_SCORE = 777;

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use('/static', express.static(path.join(__dirname, 'static')));

// --- MIDDLEWARES ---
const auth = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) {
        if(req.path.startsWith('/api/')) return res.status(401).json({error: "Unauthorized"});
        return res.redirect('/static/index.html');
    }
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        const user = db.getUserById(decoded.id);

        if (!user) {
            res.clearCookie('token');
            if (req.path.startsWith('/api/')) return res.status(401).json({ error: "Invalid session: user not found" });
            return res.redirect('/static/index.html?error=InvalidSession');
        }
        req.user = { id: user.id, username: user.username, score: user.score, hints: user.hints, plays: user.plays };
        next();
    } catch (e) {
        res.clearCookie('token');
        return res.redirect('/static/index.html');
    }
};

const requireAdmin = (req, res, next) => {
    const token = req.cookies.adminToken;
    if (!token) return res.status(401).json({ error: "Unauthorized" });
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        if (decoded.role !== 'admin' || decoded.id !== 999999 || decoded.username !== 'Bot') return res.status(403).json({ error: "Forbidden" });
        req.admin = decoded;
        next();
    } catch (e) {
        return res.status(401).json({ error: "Invalid token" });
    }
};

// --- FUNCTIONS ---

function getCorrectMove(userId, numberOfPlays) { 
    const input = `${userId}:${numberOfPlays}:${GAME_SEED}`;
    const hash = crypto.createHmac('sha256', GAME_SEED).update(input).digest('hex');

    const lastChar = parseInt(hash.slice(-1), 16);
    return (lastChar % 2 === 0) ? 'cross' : 'wait';
}

// --- ROUTES ---

app.get('/', auth, (req, res) => {
    res.redirect('/static/index.html');
});

app.get('/api/me', auth, (req, res) => {
    const user = req.user;
    
    let returnedFlag = null;
    if (user.score >= TARGET_SCORE) {
        returnedFlag = FLAG;
    }
    res.json({ 
        username: user.username, 
        score: user.score, 
        hints: user.hints, 
        flag: returnedFlag 
    });
});

app.post('/api/play', auth, (req, res) => {
    const action = req.body.action;
    if (!['cross', 'wait'].includes(action)) return res.status(400).json({ error: "Invalid action" });

    const user = req.user;
    const safeMove = getCorrectMove(user.id, user.plays);
    db.incrementPlays(user.id);

    if (action === safeMove) {
        const points = (action === 'cross') ? 69 : 1;
        db.updateScore(user.id, user.score + points);
        return res.json({ status: "safe", gained: points });
    } else {
        db.resetScore(user.id);
        return res.json({ status: "fail" });
    }
});

app.get('/api/adminPlay', auth, requireAdmin, (req, res) => {
    const action = 'cross'; // Admin always crosses

    const user = req.user;
    const safeMove = getCorrectMove(user.id, user.plays);

    if (action === safeMove) {
        return res.json({ status: "safe" });
    } else {
        return res.redirect('/static/gameOver.html'); // Back to lobby noob
    }
});

app.post('/api/hint', auth, (req, res) => {
    let url = req.body.url;
    const user = req.user;
    const token = req.cookies.token;

    if (!url) res.json({ msg: 'Missing URL' });

    if(typeof url !== 'string'){
        res.json({ msg: 'Invalid URL' });
    }
    browse(url, user, token).then((botResponse) => { 
        res.json({ msg: botResponse });
    }) // no catch...I handle my own errors!
});

app.post('/api/register', (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).send("Missing fields");
    
    const result = db.createUser(username, password);
    if (result) return res.redirect('/static/index.html');
    res.status(400).send("User already exists");
});

app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    
    const user = db.verifyUser(username, password);
    if (user) {
        const token = jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '2h' });

        res.cookie('token', token, { 
            httpOnly: true, 
            sameSite: 'Lax',
            maxAge: 7200000 
        });
        return res.redirect('/static/game.html');
    }
    res.redirect('/static/index.html?error=InvalidCredentials');
});

app.listen(PORT, '0.0.0.0', () => console.log(`Media Meeting running on ${PORT}`));