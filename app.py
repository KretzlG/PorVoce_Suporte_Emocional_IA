from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('register')) 
# Pelo amor de Deus, me lembra de adicionar um verificador pra ver se o usuário já está logado ou não.

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
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

if __name__ == '__main__':
    app.run(debug=True)