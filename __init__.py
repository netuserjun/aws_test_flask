# -*- coding: utf-8 -*-
import os, sys
from runpy import run_module
from flask import Flask, escape, request,  Response, g, make_response, send_file, jsonify
import logging
from flask.templating import render_template
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
""" from . import face_morph_python
from . import face_extractor
from . import pattern_generator"""
from . import crawl 
import socket
import subprocess
import glob
import io
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime

#FLAGS = flags.FLAGS
#flags.DEFINE_string("input_directory", "static/images/input_images", "input directory containing all the images")
#flags.DEFINE_string("face_directory", "static/images/face_images", "output directory containing the extracted faces")
#LANDMARKS_MODEL_URL = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'

app = Flask(__name__)
app.debug = True
#logging.basicConfig(filename='flask.log', level=logging.DEBUG)
# Main page
@app.route('/')
def index():
    return render_template('index.html')

labels = ["1. 쇼핑몰의 로그인 URL","2. ID","3. PW","4. ID selector","5. PW selector","6. login버튼 selector","7. 검색 url","8. 검색결과 클릭용 selector"]
num_inputs = 8

@app.route('/crawl_ready', methods=['GET', 'POST'])
def crawl_ready():
    host_ip = request.remote_addr
    os.makedirs('/home/ec2-user/pyflask/src/finish/%s'%host_ip,exist_ok=True)
    #os.makedirs('/home/ec2-user/pyflask/src/finish/%s/log/',exist_ok=True)
    #os.makedirs('/home/ec2-user/pyflask/src/finish/%s/crawl/',exist_ok=True)
    now = datetime.now()
    now = str(now).split(".")[0].replace("-","").replace(" ","").replace(":","")
    new_log_directory = "log" + str(now)
    new_crawl_directory = "crawl" + str(now)
    os.system('mv /home/ec2-user/pyflask/src/log/%s/ /home/ec2-user/pyflask/src/finish/%s/%s'%(host_ip,host_ip,new_log_directory))
    os.system('mv /home/ec2-user/pyflask/src/out/%s/ /home/ec2-user/pyflask/src/finish/%s/%s'%(host_ip,host_ip,new_crawl_directory))

    if request.method == "POST":
        texts = []
        targets = []
        file = request.files['file']
        file_contents = file.read().decode("utf-8")
        lines = file_contents.rstrip().split("\r\n")
        targets.extend(lines)

        for label in labels[:num_inputs]:
            texts.append((label, request.form[label.lower()]))
            

        return redirect(url_for("crawl_start", texts = texts, targets=targets))

    return render_template("crawl_ready.html", labels=labels[:num_inputs])
@app.route("/log")
def log():
    client_ip = request.remote_addr
    with open("/home/ec2-user/pyflask/src/log/%s/script_output.log"%client_ip, "r") as f:
        log = f.read()
    return log
'''
@app.route("/output")
def output():
    cmd = "ls -l"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return jsonify(output=output.decode("utf-8"))
'''
'''@app.route("/run_script")
def run_script():
    with open("output.log", "w") as log_file:
        sys.stdout = log_file
        print("This is a print statement")
        sys.stdout = sys.__stdout__
    return "Script run complete"

@app.route("/output")
def output():
    with open("output.log", "r") as log_file:
        return log_file.read()'''

@app.route("/crawl_start")
def crawl_start():
    texts = request.args.getlist("texts")
    targets = request.args.getlist("targets")
    #print(texts)
    texts = [text.replace("(","").replace(")","").replace("'","") for text in texts]
    texts = [text.split(",") for text in texts]
    #print(texts)
    host_ip = request.remote_addr
    product_count = crawl.main(texts,host_ip,targets)
    print(product_count)
    return render_template("crawl_start.html", product_count=product_count)

@app.route("/download")
def download():
    # Create a zip file in memory
    in_memory = io.BytesIO()
    with ZipFile(in_memory, "w") as zf:
        # Add all files in the folder to the zip file
        client_ip = request.remote_addr
        folder_to_compress = "/home/ec2-user/pyflask/src/out/%s"%client_ip
        root_len = len(os.path.abspath(folder_to_compress))
        for root, dirs, files in os.walk(folder_to_compress):
            for file in files:
                abs_path = os.path.abspath(os.path.join(root, file))
                relative_path = abs_path[root_len + 1:]
                zf.write(abs_path, relative_path)
    # Set the file name and headers
    in_memory.seek(0)
    #headers = {"Content-Disposition": "attachment;filename=compressed_folder.zip"}
    return send_file(in_memory, download_name="%s_Crawling.zip"%client_ip, as_attachment=True)
