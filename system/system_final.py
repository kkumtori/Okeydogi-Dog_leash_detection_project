###################### environments #############################
import cv2
import time
from playsound import playsound
import numpy as np
import torch
from PIL import Image
from tensorflow import keras###
from keras.applications.resnet_v2 import preprocess_input###
from keras.utils import img_to_array
from keras.models import load_model
import paramiko
from datetime import datetime
import pymysql
from sshtunnel import SSHTunnelForwarder
################### Server #############################
host = "18.180.41.193"
port = 22
transprot = paramiko.transport.Transport(host,port)
userId = "lab15"
key = paramiko.RSAKey.from_private_key_file('/home/sesac/poppy/SeSAC_Group4.pem')
transprot.connect(username = userId, pkey=key)
sftp = paramiko.SFTPClient.from_transport(transprot)
remotepath = '/home/lab15/web/static/assets/images/capture/'
################## DB #################################
tunnel = SSHTunnelForwarder(("18.180.41.193", 22), ssh_username='lab15', ssh_pkey='/home/sesac/poppy/SeSAC_Group4.pem', remote_bind_address=('127.0.0.1', 8945))
tunnel.start()
conn = pymysql.connect(host='127.0.0.1', user='sesac', passwd='1111', db='project', charset='utf8', port=tunnel.local_bind_port)
cursor = conn.cursor()
sql = "INSERT INTO dog (filename, location, time) VALUES (%s, %s, %s)"
################### YOLO model ##########################
print('yolo-start')
playsound("/home/sesac/poppy/yolo.wav")
yolo_model = torch.hub.load('WongKinYiu/yolov7', 'custom','/home/sesac/poppy/0213_yolov7_epochs55.pt', force_reload=False)
yolo_model.conf=0.6 # thresghold
yolo_model.classes=27
yolo_model.iou=0.6
################### CNN model ############################
print('cnn-start')
playsound("/home/sesac/poppy/cnn.wav")
model = load_model("/home/sesac/poppy/0217_aug_flip")
idx_to_classes = {0: 'with-leash', 1: 'without-leash'}
################### FUNCTIONS #####################################
def capture():
	while True:
		webcam=cv2.VideoCapture(0)
		while True :
			ret, frame = webcam.read()
			results = yolo_model(frame, size=416)
			pos_lists = results.pandas().xyxy
			pos_df = pos_lists[0]  
			dogs=pos_df[['xmin', 'ymin', 'xmax', 'ymax']]
            confidences=pos_df['confidence']
			if len(dogs) >= 1 :
				break
		for i in range(len(dogs)):
            dog=dogs.iloc[i].tolist()
            dog=list(map(int,dog))
            conf=confidences.iloc[i]     
			now = datetime.now()
			name = now.strftime('%y%m%d%H%M%S') + '.jpg'
			xmin,ymin,xmax,ymax=dog
            margin=20
            height=frame.shape[0]
            width=frame.shape[1]
			cv2.imwrite(name,frame[max(ymin-margin,0):min(ymax+margin,height),max(xmin-margin,0):min(xmax+margin,width),:])
			ret = pred('/home/sesac/poppy/capture/' + name,probs=True)
			if(ret == 'without-leash') :
				playsound("/home/sesac/poppy/alert_final.wav")
				sftp.put('/home/sesac/poppy/capture/' + name, remotepath + name)
				cursor.execute(sql, (name, "sesac", now))
				conn.commit()
				print('without-leash-detect!!!!')
		webcam.release()
		time.sleep(1)
	webcam.release()
	sftp.close()
	transprot.close()
	conn.close()
# CNN pred
def pred(img_path,probs=False):
    img = keras.preprocessing.image.load_img(img_path, target_size=(224,224))
    array = keras.preprocessing.image.img_to_array(img) #(224,224,3)
    array = np.expand_dims(array, axis=0)  #(1, 224, 224, 3)
    img_array = preprocess_input(array)
    preds = model.predict(img_array)
    if probs:
        print('with vs without :',preds)
    return idx_to_classes[np.argmax(preds)]

playsound("/home/sesac/poppy/execute.wav")
capture()
