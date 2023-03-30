from ctypes import *
import random
import os
import cv2
import time
import datetime
import darknet
import argparse
import urllib.request
import sys
import re 
import csv
import xlsxwriter
from xlrd import open_workbook
from xlutils.copy import copy 
from threading import Thread, enumerate
from queue import Queue
from flask import Flask, render_template, Response, request, redirect, url_for
from threading import Thread
from flask import Flask, render_template, Response 
from openpyxl import load_workbook
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates', static_url_path='/static')

picFolder = os.path.join('static', 'video', 'breedvideo')
app.config['UPLOAD_FOLDER'] = picFolder

cam = cv2.VideoCapture(1) 

global rec_frame, switch, rec, out
switch = 1
rec = 0

def record(out):
     while (rec):
         time.sleep(0.05)
         out.write(rec_frame)
    

class YOLOv4Behavior:
    global switch, camera
    def __init__(self):
        self.initialize_network()
    def initialize_network(self):

        self.net = cv2.dnn_DetectionModel('cfg/yolov4-obj-behavior.cfg', 'backup4behavior/yolov4-obj_last.weights')

        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.net.setInputSize(416, 416)
        self.net.setInputScale(1.0 / 255)
        self.net.setInputSwapRB(True)
        with open('data/lstm.names', 'rt') as f: 
            self.names = f.read().rstrip('n').split('\n')

    global rec_frame, switch, rec, out
    switch = 1
    rec = 0

    def record(out):
        while (rec):
            time.sleep(0.05)
            out.write(rec_frame)

    def run_interference(self):
        global out, capture, rec_frame
        source = cv2.VideoCapture(1)
        now = datetime.datetime.now()
        with open('static/csv/behaviordata_{}.csv'.format(str(now).replace (":", '')),"w") as f1:
            cwriter = csv.writer(f1)
            cwriter.writerow(['Timestamp', 'Classification', 'Confidence'])
            while(source.isOpened()):
        
                success, frame = source.read()
                if success: 
                    if (rec):
                        rec_frame = frame
                        frame = cv2.putText(cv2.flip(frame, 1), "Rec...", (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 4)
                        frame = cv2.flip(frame, 1)
                        timer = time.time()
                        detections=[]
                        classIds, confidences, boxes = self.net.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
                        print('[INFO] Time Taken: {} | FPS: {}'.format(time.time() - timer, 1/(time.time() - timer)), end='\r')
                    
                    if len(classIds) != 0:
                        for classId, confidence, box in zip(classIds.flatten(), confidences.flatten(), boxes):
                            if confidence > 0.5: 
                                label = '%s: %.2f' % (self.names[classId], confidence)
                                left, top, width, height = box
                                b = random.randint(0, 255)
                                g = random.randint(0, 255)
                                r = random.randint(0, 255)
                                cv2.rectangle(frame, box, color=(b, g, r), thickness=2)
                                cv2.rectangle(frame, (left, top), (left + len(label) * 20, top - 30), (b, g, r), cv2.FILLED)
                                cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_COMPLEX, 1, (255 - b, 255 - g, 255 - r), 1, cv2.LINE_AA)
                        cwriter.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.names[classId],confidence])
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: imagem/jpeg\r\n\r\n' + frame + b'\r\n')    

class YOLOv4Breed:
    global switch, camera
    def __init__(self):
        self.initialize_network()
    def initialize_network(self):

        self.net = cv2.dnn_DetectionModel('cfg/yolov4-obj.cfg', 'backup4breed/yolov4-obj_last.weights')

        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.net.setInputSize(416, 416)
        self.net.setInputScale(1.0 / 255)
        self.net.setInputSwapRB(True)
        with open('data/obj.names', 'rt') as f: 
            self.names = f.read().rstrip('n').split('\n')

    global rec_frame, switch, rec, out
    switch = 1
    rec = 0

    def record(out):
        while (rec):
            time.sleep(0.05)
            out.write(rec_frame)

    def run_interference(self):
        global out, capture, rec_frame
        source = cv2.VideoCapture(1)
        now = datetime.datetime.now()
        with open('static/csv/Breeddata_{}.csv'.format(str(now).replace (":", '')),"w") as f1:
            cwriter = csv.writer(f1)
            cwriter.writerow(['Timestamp', 'Classification', 'Confidence'])
            while(source.isOpened()):

                success, frame = source.read()
                if success: 
                    if (rec):
                        rec_frame = frame
                        frame = cv2.putText(cv2.flip(frame, 1), "Rec...", (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 4)
                        frame = cv2.flip(frame, 1)
                        timer = time.time()
                        detections=[]
                        classIds, confidences, boxes = self.net.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
                        print('[INFO] Time Taken: {} | FPS: {}'.format(time.time() - timer, 1/(time.time() - timer)), end='\r')
                    
                    if len(classIds) != 0:
                        for classId, confidence, box in zip(classIds.flatten(), confidences.flatten(), boxes):
                            if confidence > 0.5: 
                                label = '%s: %.2f' % (self.names[classId], confidence)
                                left, top, width, height = box
                                b = random.randint(0, 255)
                                g = random.randint(0, 255)
                                r = random.randint(0, 255)
                                cv2.rectangle(frame, box, color=(b, g, r), thickness=2)
                                cv2.rectangle(frame, (left, top), (left + len(label) * 20, top - 30), (b, g, r), cv2.FILLED)
                                cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_COMPLEX, 1, (255 - b, 255 - g, 255 - r), 1, cv2.LINE_AA)
                        cwriter.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.names[classId],confidence])
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: imagem/jpeg\r\n\r\n' + frame + b'\r\n')  
        f1.close()

            
@app.route('/requests', methods=['POST', 'GET'])
def recording():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec = not rec
            if (rec):
                now = datetime.datetime.now()
                fourcc = cv2.VideoWriter_fourcc(*'X264')
                out = cv2.VideoWriter('static/videos/behaviorvid_{}.mp4'.format(str(now).replace(":", '')), fourcc, 20.0, (640, 480))
                thread = Thread(target=YOLOv4Behavior.record, args=[out, ])
                thread.start()
            else:
                out.release()

    elif request.method == 'GET':
        return render_template('Behavior.html')
    return render_template('Behavior.html', )

@app.route('/breedrequests', methods=['POST', 'GET'])
def breedrecording():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec = not rec
            if (rec):
                now = datetime.datetime.now()
                fourcc = cv2.VideoWriter_fourcc(*'X264')
                out = cv2.VideoWriter('static/videos/breedvid_{}.mp4'.format(str(now).replace(":", '')), fourcc, 20.0, (640, 480))
                thread = Thread(target=YOLOv4Breed.record, args=[out, ])
                thread.start()
            else:
                out.release()

    elif request.method == 'GET':
        return render_template('Breed.html')
    return render_template('Breed.html', )

@app.route('/')
def welcome():
    return render_template('Welcome.html')

@app.route('/behavior')
def behavior():
    return render_template('Behavior.html')

@app.route('/video')
def video():
    return Response(YOLOv4Behavior().run_interference(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/breed')
def breed():
    return render_template('Breed.html')

@app.route('/breedvideo')
def breedvideo():
    return Response(YOLOv4Breed().run_interference(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/gallery')
def gallery():
    imageList = os.listdir('static/videos')
    imagelist = ['videos/' + image for image in imageList]
    return render_template('Gallery.html', imagelist=imagelist)

@app.route('/about')
def about():
    return render_template('About.html')


if __name__=="__main__":
    yolo = YOLOv4Behavior().__new__(YOLOv4Behavior)
    yolo2 = YOLOv4Breed().__new__(YOLOv4Breed)
    yolo.__init__()
    yolo2.__init__()
    app.run(debug=True)