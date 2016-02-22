import tempfile
import json, base64, os
from flask import Flask, request, Response, abort, redirect, url_for, jsonify
from hashlib import md5
import StringIO
import magic
from dropbox_sync import *
from PIL import Image
import sys

print "Reading path"
path = sys.argv[1]
print path


def resize(filename):
    file_path = path + "/" + filename
    try:
        image = Image.open(file_path)
        resize_img = image.save("/home/nhuan/MyWorking/storage_service/storage/" + filename + "_75", "JPEG", quality=75)
    except Exception as e:
        print e
        print filename
    return "OK"


try:
    for file_name in os.listdir(path):
        print file_name
        hash_name = md5(file_name).hexdigest()
        resize(file_name)
except Exception as e:
    print e
