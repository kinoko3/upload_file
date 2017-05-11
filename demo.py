from flask import Flask, render_template, flash, redirect, url_for, request, send_from_directory
from flask_bootstrap import Bootstrap
import config, os, simplejson
from lib.upload_file import uploadfile
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(config)
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

                size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 获取文件大小

                result = uploadfile(name=filename, type=mime_type, size=size)  # 调取上传文件信息类类
                print(result.get_file())

            return simplejson.dumps({"files": [result.get_file()]})
    if request.method == 'GET':#获取已经上传的文件在下方列出
        '''
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if

                 os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]
        '''
        files = os.listdir(app.config['UPLOAD_FOLDER'])#获取文件列表

        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))#文件大小
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

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

@app.route("/data/<string:filename>", methods=['GET'])#下载功能
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=9191)

