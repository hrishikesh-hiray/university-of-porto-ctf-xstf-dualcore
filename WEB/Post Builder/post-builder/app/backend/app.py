from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Post
import uuid
import requests
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
PUBLIC_WEB_URL = os.environ.get('WEB_URL', 'http://127.0.0.1:5001').rstrip('/')

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

CORS(app, supports_credentials=True, origins='*')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@postbuilder.local')
        admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
        db.session.add(admin)
        db.session.commit()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400

    if len(data['username']) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400

    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    login_user(user)

    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    login_user(user, remember=data.get('remember', False))

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({'user': current_user.to_dict()}), 200

@app.route('/api/posts', methods=['GET'])
@login_required
def get_posts():
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts]), 200

@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify(post.to_dict()), 200

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()

    if not data or not all(k in data for k in ['title', 'layout']):
        return jsonify({'error': 'Missing required fields'}), 400

    post_id = str(uuid.uuid4())
    post = Post(
        id=post_id,
        title=data['title'],
        user_id=current_user.id
    )
    post.set_layout(data['layout'])

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201

@app.route('/api/posts/<post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if post.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(post)
    db.session.commit()

    return jsonify({'message': 'Post deleted'}), 200

@app.route('/api/report', methods=['POST'])
@login_required
def report_post():
    data = request.get_json()

    if not data or 'postId' not in data:
        return jsonify({'error': 'Missing postId'}), 400

    post_id = data['postId']
    post = Post.query.get(post_id)

    if not post:
        return jsonify({'error': 'Post not found'}), 404

    try:
        bot_url = 'http://localhost:8000/visit'
        web_url = f'{PUBLIC_WEB_URL}/post/{post_id}'

        response = requests.post(bot_url, json={'url': web_url}, timeout=5)

        if response.status_code == 200:
            return jsonify({'message': 'Post reported successfully. Admin will review it shortly.'}), 200
        else:
            return jsonify({'error': 'Failed to report post'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
