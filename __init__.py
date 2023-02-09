import os, sys
from runpy import run_module
from flask import Flask, escape, request,  Response, g, make_response, send_file
from flask.templating import render_template
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
""" from . import face_morph_python
from . import face_extractor
from . import pattern_generator"""
from . import crawl 
from absl import flags
from absl import app
import glob
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

FLAGS = flags.FLAGS
#flags.DEFINE_string("input_directory", "static/images/input_images", "input directory containing all the images")
#flags.DEFINE_string("face_directory", "static/images/face_images", "output directory containing the extracted faces")
#LANDMARKS_MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
 
app = Flask(__name__)
app.debug = True
 
# Main page
@app.route('/')
def index():
    return render_template('index.html')

labels = ["쇼핑몰의 로그인 URL","ID","PW","ID selector","PW selector","login버튼 selector","검색 url","상품명","검색결과 클릭용 selector","결과저장폴더의 절대경로"]
num_inputs = 10

@app.route('/crawl_ready', methods=['GET', 'POST'])
def crawl_ready():
    if request.method == "POST":
        texts = []
        for label in labels[:num_inputs]:
            texts.append((label, request.form[label.lower()]))
            

        return redirect(url_for("crawl_start", texts = texts))

    return render_template("crawl_ready.html", labels=labels[:num_inputs])

@app.route("/crawl_start")
def crawl_start():
    texts = request.args.getlist("texts")
    #print(texts)
    texts = [text.replace("(","").replace(")","").replace("'","") for text in texts]
    texts = [text.split(",") for text in texts]
    #print(texts)
    crawl.main(texts)
    return render_template("crawl_start.html", texts=texts)


