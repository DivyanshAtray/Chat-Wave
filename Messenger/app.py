from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/messenger'
db = SQLAlchemy(app)
socketio = SocketIO(app)

class Signin(db.Model):
    Serialno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(20), nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    Date = db.Column(db.String(10), nullable=True)

@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            return "All fields are required!", 400

        entry = Signin(Name=name, Email=email, Password=password, Date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('sign-in.html')

@app.route("/index", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_send_message(data):
    email = data['email']
    message = data['message']
    
    # Fetch the username from the database based on the email
    user = Signin.query.filter_by(Email=email).first()

    if user:
        username = user.Name
    else:
        username = 'Unknown User'

    # Emit the message with the username to all connected clients
    emit('receive_message', {'username': username, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
