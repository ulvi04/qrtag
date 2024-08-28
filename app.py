from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secret key in production

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user in the database
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error='Invalid Credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        # Create a new user and add it to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    qr_data = None  # Initialize QR data to None
    if request.method == 'POST':
        # Capture user details from the form
        name = request.form.get('name')
        surname = request.form.get('surname')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        instagram = request.form.get('instagram', '')
        facebook = request.form.get('facebook', '')

        # Combine all details into a single string for QR code
        qr_data = f"Name: {name}\nSurname: {surname}\nMobile: {mobile}\nEmail: {email}\n"
        if instagram:
            qr_data += f"Instagram: {instagram}\n"
        if facebook:
            qr_data += f"Facebook: {facebook}"

        # Generate the QR code
        qr = qrcode.make(qr_data)
        
        # Save QR code to a BytesIO object
        qr_io = io.BytesIO()
        qr.save(qr_io, 'PNG')
        qr_io.seek(0)
        
        # Encode the QR code as base64 to display in HTML
        qr_data = base64.b64encode(qr_io.getvalue()).decode('utf-8')

    return render_template('profile.html', username=session['username'], qr_data=qr_data)

@app.route('/download_qr', methods=['POST'])
def download_qr():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Generate the QR code again for download
    name = request.form.get('name')
    surname = request.form.get('surname')
    mobile = request.form.get('mobile')
    email = request.form.get('email')
    instagram = request.form.get('instagram', '')
    facebook = request.form.get('facebook', '')

    qr_data = f"Name: {name}\nSurname: {surname}\nMobile: {mobile}\nEmail: {email}\n"
    if instagram:
        qr_data += f"Instagram: {instagram}\n"
    if facebook:
        qr_data += f"Facebook: {facebook}"

    qr = qrcode.make(qr_data)
    
    # Save QR code to a BytesIO object
    qr_io = io.BytesIO()
    qr.save(qr_io, 'PNG')
    qr_io.seek(0)
    
    return send_file(qr_io, mimetype='image/png', as_attachment=True, download_name=f'{session["username"]}_qr.png')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
