import tempfile
import json,base64,os
from flask import Flask, request,Response,abort, redirect, url_for,jsonify
from hashlib import md5
import Image
import StringIO
import magic
from PIL import Image

app = Flask(__name__)
folder_name = os.getcwd()+"/storage"
port = os.getenv('VCAP_APP_PORT', '8080')

app.config["UPLOAD_FOLDER"]='storage/'
app.config["ALLOWED_EXTENSION"]=set(['jpg','jpeg','png','gif','bmp'])
app.config["MAX_FILE_SIZE"]= 5000000 #5MB
def validate_ext(file):
    mimetype = magic.from_buffer(file.stream.read(),mime=True)
    ext = mimetype.rsplit('/',1)[1]
    result = ext in app.config["ALLOWED_EXTENSION"]
    return result
def validate_size(file):
    chunk = 10
    data = None
    size = 0
    while data != b'':
        data = file.read(chunk)
        size+= len(data)
        if (size> app.config["MAX_FILE_SIZE"]):
            return False
    return True
def resize(filename):
    #fad
    file_path = app.config["UPLOAD_FOLDER"]+filename
    image = Image.open(file_path)
    resize_img = image.save(app.config["UPLOAD_FOLDER"]+filename+"_75","JPEG",quality=75)
@app.route('/')
def hello_world():
    return 'Hello World! I am running on port ' + str(port)

@app.route('/upload',methods=["POST"])
def upload():
    file = request.files["file"]
    hash_name = md5(file.filename).hexdigest()
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],hash_name))
        resize(file.filename)
        return jsonify({"filename": hash_name})
    else:
        return jsonify({"key":"Error cannot save"})

@app.route('/<path:filename>',methods=["GET"])
def load_image(filename):

    file_path = app.config["UPLOAD_FOLDER"]+filename
    mimetype = magic.from_file(file_path,mime=True)
    ext = mimetype.rsplit('/',1)[1]
    try:

        im = Image.open(file_path)
        io = StringIO.StringIO()
        im.save(io,format=ext.capitalize())
        return Response(io.getvalue(),mimetype=mimetype)
    except IOError:
        abort(404)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int(port)
    )






