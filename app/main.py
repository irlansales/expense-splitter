from flask import Blueprint, render_template, request

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        senha = request.form['senha']
        return f'login recebido: {email}'


    return render_template('login.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       email = request.form ["email"]
       senha = request.form ['senha']
       return f'cadastro recebido: {email}'

    return render_template('register.html')