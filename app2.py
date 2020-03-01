# coding: utf-8

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename

from skimage.io import imread
from skimage.filters import threshold_otsu
import matplotlib.pyplot as plt


import os, io, time, re

# # MODEL_FILE_PATH = 'model_corona_002auto.ftz'

# #　flask appを使えるようにするためのインスんタンス化
# app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False  # 日本語文字ばけ防止

# @app.route('/', methods=["GET", "POST"])
# def post_json():
#     if  request.method == "GET":
#         return 'Hello, World!'
    
   

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

from flask import Flask
app = Flask(__name__)



@app.route('/',methods=('POST','GET'))
def hello_world():
 if  request.method == "GET":
      return 'Get Hello, World!'
    
 elif request.method == "POST":
      return  'Post Hello, World!'  

            

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
