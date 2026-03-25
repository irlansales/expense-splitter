from flask import Blueprint, render_template, request
from app import db
from app.models import Usuario

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form["email"]
        senha = request.form['senha']
        return f'login recebido: {email}'


    return render_template('login.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form ["nome"]
        email = request.form ["email"]
        senha = request.form ['senha']

        print(f"Salvando: {nome}, {email}")  # ← E isso


        novo_usuario = Usuario(nome=nome, email=email, senha=senha)

        db.session.add(novo_usuario)    
        db.session.commit()
        print("SALVO NO BANCO!")    

        return f'cadastro recebido: {nome} email: {email} hehe'

    return render_template('register.html')