import sys
import json
from tensorflow import keras
import matplotlib.pyplot as plt
import tensorflow as tf
import cv2
import string
import imutils
import numpy as np

htr = tf.keras.models.load_model(r"C:\Users\nithi\Downloads\handwriting-assessment-master\handwriting-assessment-master\htr.h5")

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    i = 0
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
    key=lambda b:b[1][i], reverse=reverse))
    return (cnts, boundingBoxes)

d = dict.fromkeys(string.ascii_lowercase, 0)
count = 0 
mean_score = 0
summation = 0

def final(img):
    
    letters = []
    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # plt.imshow(gray)
    # plt.show()
    ret,thresh1 = cv2.threshold(gray ,127,255,cv2.THRESH_BINARY_INV)
    dilated = cv2.dilate(thresh1, None, iterations=2)

    cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sort_contours(cnts, method="left-to-right")[0]
    for c in cnts:

        if cv2.contourArea(c) > 10:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = gray[y:y + h, x:x + w]
        thresh = cv2.threshold(roi, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        thresh = cv2.resize(thresh, (28, 28), interpolation = cv2.INTER_CUBIC)
        thresh = thresh.astype("float32") / 255.0
        thresh = np.expand_dims(thresh, axis=-1)
        thresh = thresh.reshape(1,28,28,1)
        ypred = htr.predict(thresh)

        alphabets="abcdefghijklmnopqrstuvwxyz"
        list1=[]
        [list1.append(i) for i in range(26)]
        list2=[]
        [list2.append(i) for i in alphabets]
        dic = dict(zip(list1, list2))
        score = np.argmax(ypred)
        score = ypred[0,score]
        score = round((score*100), 4)
        for key in d:
            if d[key] == 0:
                if key == dic[np.argmax(ypred)]:
                    d[key] = round(score, 2)
            else:
                if key == dic[np.argmax(ypred)]:
                    d[key] += round(score, 2)
                    d[key] /= 2
    
        summation = sum(d.values())
        count = 0
        for key, value in d.items():
            if value != 0:
                count += 1
        mean_score = summation/count
    

    dic_out1 = {x:y for x,y in d.items() if y!=0}
    dic_out2 = {x:y for x,y in dic_out1.items() if float(y)<90}
    dic_out3 = {x:y for x,y in dic_out2.items() if float(y)>80}
    grade = ''
    if(mean_score > 97):
        dic_out3['grade'] = 'a'
        dic_out3['message'] = 'Outstanding'
    elif(mean_score > 90 and mean_score < 97):
        dic_out3['grade'] = 'b'
        dic_out3['message'] = 'You can do better'
    else:
        dic_out3['grade'] = 'c'
        dic_out3['message'] = 'Practice More'
    
    #print(dic_out3)
    jsonObj = json.dumps(dic_out3)
    print(jsonObj)
    #print("Score: ", mean_score)
        
filename = sys.argv[1]
# filename = 'name.jpg'
pathFolder = r"C:\Users\nithi\Downloads\handwriting-assessment-master\handwriting-assessment-master\upload_images\\" + filename
final(pathFolder)