from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from functools import wraps
from app.models.wordlists import low_risk, medium_risk, high_risk

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secretinha_owo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações DataBase e Login
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

login_manager.login_message = "Por favor, faça login para acessar esta página."

# Banco de dados simples (apenas para login e registro)
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')

        if not token:
            return jsonify({"message": "Token não encontrado!"}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({"message": "Token inválido!"}), 401
        
        return  f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/')
def index():
        return redirect(url_for('register'))	
     

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    return render_template('index.html', username=current_user.username)


#Atualizações futuras: Se o usuário já estiver logado, ele não pode acessar a pagina de login ou registro.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if Users.query.filter_by(username=username).first() or Users.query.filter_by(email=email).first():
            flash("Usuário ou email já existe.")
            return redirect(url_for("register"))
        
        if password != confirm_password:
            flash("As senhas não coincidem.")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = Users(username=username, password=hashed_password, public_id=str(uuid.uuid4()), email=email)
        
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    return render_template("register.html")
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Email ou senha incorretos.', 'error')
            return redirect(url_for('login'))

        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                           app.config['SECRET_KEY'], algorithm="HS256")

        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('jwt_token', token)

        login_user(user)

        return response

    return render_template('login.html')

@app.route('/diary')
def diary():
    return render_template('diary.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/logout')
@login_required
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('jwt_token')
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return response

# Verificação de status mental
@app.route('/API/triage', methods=['POST'])
def triage():
    if request.method == 'POST':
        message = request.form['chatTexto'].lower()

        if any(word in message for word in low_risk):
            response = "Parece que você está passando por um momento difícil. Se precisar, estou aqui para conversar."
            return jsonify({"message": response, "user_message": message},
                           {"risk":"low"})
        
        elif any(word in message for word in medium_risk):
            response = "Sua mensagem indica que você pode estar enfrentando problemas sérios. É importante buscar ajuda profissional."
            return jsonify({"message": response, "user_message": message},
                           {"risk":"medium"})
        
        elif any(word in message for word in high_risk):
            response = "Sua mensagem sugere que você pode estar em perigo. Por favor, procure ajuda imediatamente."
            return jsonify({"message": response, "user_message": message},
                           {"risk":"high"})
    
    return jsonify({"message": "Nenhum risco identificado.", "user_message": message},
                   {"risk": "none"})
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)