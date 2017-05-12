import os
SECRET_KEY = os.urandom(8)
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file/')
ALLOWED_EXTENSIONS = set(['txt', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'rar', 'zip', '7zip', 'doc', 'docx'])
