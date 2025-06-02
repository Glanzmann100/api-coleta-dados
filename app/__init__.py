from flask import Flask
from flask import request, jsonify, redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/Create_User', methods=['POST'])
def Create_User():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']

    if password != password2:
        return render_template('index.html', error='Passwords do not match!', name=name, email=email)

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return render_template('index.html', error='Email already registered!', name=name, email=email)

    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    users = User.query.all()
    data = [{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'password': u.password
    } for u in users]
    df = pd.DataFrame(data)
    df.to_excel("users.xlsx", index=False)

    return redirect('/')

@app.route('/User_List', methods=['GET'])
def User_List():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users]), 200

@app.route("/User/<int:id>", methods=["GET"])
def Specific(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200

@app.route('/Update_User/<int:id>', methods=['PUT'])
def Update_User(id):
    data = request.get_json()
    user = User.query.get(id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }), 200

@app.route('/Delete_User/<int:id>', methods=['DELETE'])
def Delete_User(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User successfully removed"}), 200

@app.route('/Export_Users', methods=['GET'])
def Export_Users():
    users = User.query.all()
    data = [{'ID': u.id, 'Name': u.name, 'Email': u.email} for u in users]
    df = pd.DataFrame(data)
    df.to_excel('users.xlsx', index=False)
    return jsonify({"m
