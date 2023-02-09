# Importing libraries
import cv2
import dlib
import gdown
import numpy as np
import urllib.request
from matplotlib import pyplot as plt
import mysql.connector

#sql connection
sqlconnection = mysql.connector.connect(host =  'localhost', user = 'root', password = 'mysql')
sqlcursor = sqlconnection.cursor()
try:
    sqlcursor.execute("create database facedetectproject")
    sqlcursor.execute("use facedetectproject")
    sqlcursor.execute("create table faces(Name varchar (15), url varchar (150) primary key)")
except:
    sqlcursor.execute("use facedetectproject")

'''
#Downloading dlib shape predictor
dlibshape_url = 'https://drive.google.com/uc?id=17D3D89Gke6i5nKOvmsbPslrGg5rVgOwg'
dlibshape_path ='./shape_predictor_68_face_landmarks.dat'
gdown.download(dlibshape_url, dlibshape_path, True)
'''

frontalface_detector = dlib.get_frontal_face_detector()

#Converts dlib rectangular object to bounding box co-ordinates
def rect_to_bb(rect):
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    return (x, y, w, h)

#Takes a url and converts it to an image object
def url_to_img(url):
    url_response = urllib.request.urlopen(url)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    img_obj = cv2.imdecode(img_array, -1)
    return img_obj

#displaying an image object using pyplot
def display_img(img_obj):
    plt.imshow(img_obj, interpolation='nearest')
    plt.axis('off')
    plt.show()
    plt.close()

#tries to detect face in image
def detect_face(image_url):
    global isface
    isface = None
    try:
        image = url_to_img(image_url)
        urlcheck = True
    except:
        print("Invalid URL. Please try again")
        urlcheck = False

    if urlcheck:
        isface = True
        rects = frontalface_detector(image, 1)
        if len(rects) < 1:
            print("No Face Detected")
            isface = False

        for (i, rect) in enumerate(rects):
            (x, y, w, h) = rect_to_bb(rect)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        display_img(image)


while True:
    query = input('''Please enter one out of the following options:
    1) Type 'add' to add someone's face's picture to the database
    2) Type 'get' to display someone's picture from the database
    3) Type 'quit' to end program \n''')
    if query == 'quit':
        quit()
    elif query == 'add':
        inp_url = input('Enter url of the image to be added: ')
        detect_face(inp_url)
        if isface:
            addname = input('Face has been detected. Please enter a name for this person: ')
            sqlcursor.execute("insert into faces values('%s', '%s')" %(addname, inp_url))
            print('Image location stored')
    elif query == 'get':
        searchname = input('Please enter the name of the person whose pictures you want to view: ')
        sqlcursor.execute("select url from faces where name = '%s'" %searchname)
        for x in sqlcursor:
            url_to_display = x[0]
            img_to_display = url_to_img(url_to_display)
            display_img(img_to_display)

    else:
        print('Command not recognised. Try again')
