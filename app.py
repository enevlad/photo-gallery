from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For session management

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
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
            photo_name = request.form.get('photo-name', '').strip()
            category = request.form.get('category', 'uncategorized')
            category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
            os.makedirs(category_path, exist_ok=True)
            if photo_name:
                extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{secure_filename(photo_name)}.{extension}"
            else:
                filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
            file.save(file_path)
            try:
                create_thumbnail(file_path)
                flash('File successfully uploaded')
            except Exception as e:
                flash(f'Failed to process image: {str(e)}')
                os.remove(file_path) 

            return redirect(url_for('upload'))
        else:
            flash('Invalid file type')
    return render_template('upload.html')

@app.route('/about')
def about():
    return render_template('about.html')

def create_thumbnail(image_path):
    thumbnail_size = (200, 200)
    try:
        with Image.open(image_path) as img:
            img.thumbnail(thumbnail_size)
            base, ext = os.path.splitext(image_path)
            thumbnail_path = f"{base}.thumb{ext}"
            img.save(thumbnail_path)
    except Exception as e:
        raise ValueError(f"Cannot process image file {image_path}. Error: {str(e)}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
