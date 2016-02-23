from flask import Flask, request, Response, abort, jsonify
from hashlib import md5
import magic
from dropbox_sync import *
from PIL import Image
import thread

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
def upload_controller():
    try:
        file = request.files["file"]
        hash_name = md5(file.filename).hexdigest()
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], hash_name))
            resize(hash_name)
            print "Start sync %s" % hash_name
            thread.start_new(upload, (client, "storage", "", hash_name))
            print "Finish sync"
            return jsonify({"filename": hash_name})
        else:
            return jsonify({"key": "Error cannot save"})
    except Exception as e:
        print e

@app.route('/<path:filename>',methods=["GET"])
def load_image(filename):
    try:
        file_path = app.config["UPLOAD_FOLDER"] + filename
        mimetype = magic.from_file(file_path, mime=True)
        ext = mimetype.rsplit('/', 1)[1]
        im = Image.open(file_path)
        io = StringIO()
        im.save(io,format=ext.capitalize())
        return Response(io.getvalue(),mimetype=mimetype)
    except Exception as e:
        print e
        abort(404)


@app.route('/sync')
def sync_to_dropbox():
    # upload_folder()
    delta()
if __name__ == '__main__':
    # try:
    #     # sync_folder()
    # except Exception as e:
    #     print "Error"
    app.run(
        host="0.0.0.0",
        port=int(port)
    )






