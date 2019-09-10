from flask import Flask

# UPLOAD_FOLDER = 'C:\\Users\\azrie\\Desktop\\Hackwagon\\Python\\python-exide\\uploaded_files'
UPLOAD_FOLDER = 'C:\\Users\\User\\Desktop\\New folder\\Hackwagon\\Google Drive\\uploaded'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv'])

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\azrie\\Desktop\\Hackwagon\\Python\\database.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER