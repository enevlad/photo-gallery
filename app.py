from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management

# Configuration for file uploads
UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    categories = os.listdir(app.config['UPLOAD_FOLDER'])
    images = {}
    for category in categories:
        category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
        if os.path.isdir(category_path):
            images[category] = os.listdir(category_path)
    return render_template('index.html', images=images)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('upload'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            category = request.form.get('category', 'uncategorized')
            category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
            os.makedirs(category_path, exist_ok=True)
            file_path = os.path.join(category_path, filename)
            file.save(file_path)
            create_thumbnail(file_path)
            flash('File successfully uploaded')
            return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

def create_thumbnail(image_path):
    with Image.open(image_path) as img:
        img.thumbnail((200, 200))
        thumbnail_path = f"{os.path.splitext(image_path)[0]}.thumb{os.path.splitext(image_path)[1]}"
        img.save(thumbnail_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
