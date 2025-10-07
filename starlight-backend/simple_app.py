#!/usr/bin/env python3
"""
Simple Flask backend for Starlight Blogging Website
This is a minimal version that should work without complex dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Simple in-memory storage for demo purposes
users = {}
posts = []
user_id_counter = 1
post_id_counter = 1

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        first = data.get('first')
        last = data.get('last')
        password = data.get('password')
        
        # Basic validation
        if not all([email, first, last, password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if email in users:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        global user_id_counter
        user_id = user_id_counter
        user_id_counter += 1
        
        users[email] = {
            'id': user_id,
            'email': email,
            'first': first,
            'last': last,
            'password': password  # In real app, this would be hashed
        }
        
        # Generate a simple token (in real app, use JWT)
        token = f"token_{user_id}_{email}"
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'uid': user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if email not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users[email]
        if user['password'] != password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = f"token_{user['id']}_{email}"
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'uid': user['id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts"""
    return jsonify(posts), 200

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        label = data.get('label')
        
        if not all([title, content, label]):
            return jsonify({'error': 'Title, content, and label are required'}), 400
        
        global post_id_counter
        post_id = post_id_counter
        post_id_counter += 1
        
        post = {
            'id': post_id,
            'title': title,
            'content': content,
            'label': label,
            'author': 'Demo User',  # In real app, get from token
            'created_at': '2025-01-01T00:00:00Z'
        }
        
        posts.append(post)
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Starlight backend is running'}), 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Starlight Blogging Website Backend',
        'version': '1.0.0',
        'endpoints': [
            'POST /api/register',
            'POST /api/login',
            'GET /api/posts',
            'POST /api/posts',
            'GET /api/health'
        ]
    }), 200

if __name__ == '__main__':
    print("Starting Starlight Backend Server...")
    print("Available endpoints:")
    print("  POST /api/register - Register new user")
    print("  POST /api/login - Login user")
    print("  GET /api/posts - Get all posts")
    print("  POST /api/posts - Create new post")
    print("  GET /api/health - Health check")
    print("  GET / - API info")
    print("\nServer starting on http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=True)

