from flask import Flask
from flask import request, jsonify, redirect
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Dados.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/Criar_Usuario', methods=['POST'])
def Criar_Usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']
    senha2 = request.form['senha2']

    if senha != senha2:
        return render_template('index.html', erro='As senhas não coincidem!', nome=nome, email=email)

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return render_template('index.html', erro='E-mail já cadastrado!', nome=nome, email=email)

    novo_usuario = Usuario(nome=nome, email=email, senha=senha)
    db.session.add(novo_usuario)
    db.session.commit()

    usuarios = Usuario.query.all()
    dados = [{
        'id': u.id,
        'nome': u.nome,
        'email': u.email,
        'senha': u.senha
    } for u in usuarios]
    df = pd.DataFrame(dados)
    df.to_excel("usuarios.xlsx", index=False)

    return redirect('/')

@app.route('/Lista_Usuario', methods=['GET'])
def Lista_Usuario():
    usuarios = Usuario.query.all()
    return jsonify([{'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email} for usuario in usuarios]), 200

@app.route("/Usuario/<int:id>", methods=["GET"])
def Especifico(id):
    usuario = Usuario.query.get(id)
    if usuario is None:
        return jsonify({"message": "Usuário não encontrado"}), 404
    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email
    }), 200

@app.route('/Atualizar_Usuario/<int:id>', methods=['PUT'])
def Atualizacao(id):
    data = request.get_json()
    usuario = Usuario.query.get(id)
    if usuario is None:
        return jsonify({"message": "Usuário não encontrado"}), 404
    usuario.nome = data.get('nome', usuario.nome)
    usuario.email = data.get('email', usuario.email)
    db.session.commit()
    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email
    }), 200

@app.route('/Deletar_Usuario/<int:id>', methods=['DELETE'])
def Deletar_Usuario(id):
    usuario = Usuario.query.get(id)
    if usuario is None:
        return jsonify({"message": "Usuário não encontrado"}), 404
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"message": "Usuário removido com sucesso"}), 200

@app.route('/Exportar_Usuarios', methods=['GET'])
def Exportar_Usuarios():
    usuarios = Usuario.query.all()
    dados = [{'ID': u.id, 'Nome': u.nome, 'E-mail': u.email} for u in usuarios]
    df = pd.DataFrame(dados)
    df.to_excel('usuarios.xlsx', index=False)
    return jsonify({"message": "Usuários exportados para usuarios.xlsx"}), 200

if __name__ == '__main__':
    app.run(debug=True)
