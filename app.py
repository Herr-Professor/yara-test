from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# Create the database and the users table
with app.app_context():
    db.create_all()

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Data validation function
def is_valid_username(username):
    return bool(re.match("^[A-Za-z0-9_]+$", username))

# Register or store username
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')

    if not username or not is_valid_username(username):
        return jsonify({"status": "error", "message": "Invalid username"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username already exists"}), 400

    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "User registered"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)
