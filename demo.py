from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory
from flask_bootstrap import Bootstrap
import config, os, simplejson
from lib.upload_file import uploadfile
import PIL
from PIL import Image
import traceback
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(config)
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def getdirsize(dir):
    size = 0.00
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        size = size / 1000 ** 2
    return size
def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))
        return True
    except:
        print(traceback.format_exc())
        return False


@app.route("/upload", methods=['GET', 'POST'])

def upload():
    if request.method == 'POST':
        files = request.files['file']
        if files:
            filename = files.filename

            mime_type = files.content_type  # 获取文件属性，例如text/plain

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="文件类型错误")

            else:

                files.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if mime_type.startswith('image'):
                    create_thumbnail(filename)
                size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 获取文件大小

                result = uploadfile(name=filename, type=mime_type, size=size)  # 调取上传文件信息类类
                print(simplejson.dumps({"files": [result.get_file()]}))

            return simplejson.dumps({"files": [result.get_file()]})
    if request.method == 'GET':#获取已经上传的文件在下方列出
        '''
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if

                 os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
        '''
        files = os.listdir(app.config['UPLOAD_FOLDER'])#获取文件列表
        file_display = []

        for f in files:
            file_list = os.path.splitext(f)
            if not file_list[1] == '':
                size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))#文件大小
                file_saved = uploadfile(name=f, size=size)
                file_display.append(file_saved.get_file())
        return simplejson.dumps({"files": file_display})#获取文件列表json数据
    return redirect(url_for('index'))


@app.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)

            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)

            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})

@app.route("/data/<string:filename>", methods=['GET'])#下载功能，图片是浏览功能
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    dir = app.config['UPLOAD_FOLDER']
    return render_template('index.html', dir=dir)

@app.route('/list', methods=['GET'])
def file_list():#获取已经上传的文件在下方列
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    dir = app.config['UPLOAD_FOLDER']
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    file_display = []
    for f in files:
        file_list = os.path.splitext(f)
        if file_list[1] == '':
            file_display.append(f)
    return render_template('list.html', file_display=file_display, dir=dir)
@app.route('/list/<filename>')
def jump(filename):
    foler = os.path.join(UPLOAD_FOLDER, filename)
    app.config['UPLOAD_FOLDER'] = foler#重置路径
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=9090, host="0.0.0.0")

