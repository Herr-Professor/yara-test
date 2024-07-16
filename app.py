from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import re
import logging

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "https://t.me"}})

# Set up logging
logging.basicConfig(level=logging.INFO)

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
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

# Data validation function
def is_valid_username(username):
    return bool(re.match("^[A-Za-z0-9_]+$", username))

# Store username
@app.route('/store_username', methods=['POST'])
def store_username():
    data = request.json
    username = data.get('username')
    
    if not username or not is_valid_username(username):
        return jsonify({"status": "error", "message": "Invalid username"}), 400
    
    try:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logging.info(f"Username already exists: {username}")
            return jsonify({"status": "success", "message": "Username already stored"}), 200
        
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        logging.info(f"Stored new username: {username}")
        return jsonify({"status": "success", "message": "Username stored"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error storing username: {str(e)}")
        return jsonify({"status": "error", "message": "An error occurred while storing the username"}), 500

if __name__ == '__main__':
    app.run(debug=False)