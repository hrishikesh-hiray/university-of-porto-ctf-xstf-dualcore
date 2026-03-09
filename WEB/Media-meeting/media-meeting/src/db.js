const Database = require('better-sqlite3');
const { verify } = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const db = new Database('media.db');

db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        score INTEGER DEFAULT 0,
        plays INTEGER DEFAULT 0,
        hints BOOLEAN DEFAULT TRUE
    );
`);

module.exports = {
    createUser: (username, plainPassword) => {
        try {
            const salt = bcrypt.genSaltSync(10);
            const hash = bcrypt.hashSync(plainPassword, salt);
            return db.prepare('INSERT INTO users (username, password) VALUES (?, ?)').run(username, hash);
        } catch (e) { 
            console.error(e);
            return null; 
        }
    },
    verifyUser: (username, plainPassword) => {
        const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
        if (!user) return null;
        
        if (bcrypt.compareSync(plainPassword, user.password)) {
            return user;
        }
        return null;
    },
    getUser: (username) => db.prepare('SELECT * FROM users WHERE username = ?').get(username),
    getUserById: (id) => db.prepare('SELECT * FROM users WHERE id = ?').get(id),
    updateScore: (id, score) => db.prepare('UPDATE users SET score = ? WHERE id = ?').run(score, id),
    resetScore: (id) => db.prepare('UPDATE users SET score = 0 WHERE id = ?').run(id),
    useHint: (id) => db.prepare('UPDATE users SET hints = FALSE WHERE id = ?').run(id),
    incrementPlays: (id) => db.prepare('UPDATE users SET plays = plays + 1 WHERE id = ?').run(id),
};