import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import numpy as np
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import pygame
pygame.mixer.init()
import dlib
from scipy.spatial import distance as dist

#socket package for Wireless communication bw Pycharm & ESP32
import socket
# ESP32's IP address and port
esp32_ip = ""  # Replace with your ESP32 IP address
esp32_port = 0000 # Replace with ESP32 Port

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"replaceDatabaseURL",
    'storageBucket':"replaceStorageBucket"
})

bucket=storage.bucket()

cap=cv2.VideoCapture(0) #camera changing point
cap.set(3,640)
cap.set(4,480)

imgBackground=cv2.imread('Resources/background.png')

folderModePath='Resources/Modes'
modePathList=os.listdir(folderModePath)
imgModeList=[]
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
print(len(imgModeList))

#Load the encoding file to main
print("Loading encode file...")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownWithIds
print(studentIds)
print("Encode File Loaded")

modeType=0 #
counter=0
id=-1
imgStudent=[]
stuId=[]
PresentString=''
Present_set = set()

#absentString = "4023,4043,4056,4103,4104,4109,4115,4128,321654,852741,963852"
#absentList = absentString.split(',')
#absentString = ','.join(absentList)
absentList = ['4023', '4043', '4056', '4103', '4104', '4109', '4115', '4128', '321654', '852741', '963852','1234','4321','5656','4444'] # Sample Data's
Aref = db.reference(f'Students/Absentees_Student')
Aref.child('Absentees_List').set(absentList)
Pref = db.reference(f'Students/Present_Student')
Pref.child('Present_List').set(PresentString)
#cv2.waitKey(1)

# Load the pre-trained face detector from dlib
detector = dlib.get_frontal_face_detector()
# Load the shape predictor model (download 'shape_predictor_68_face_landmarks.dat' from dlib's website)
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


# Threshold for detecting blink
EAR_THRESHOLD = 0.25
CONSECUTIVE_FRAMES = 3
blink_counter = 0

while True:
    success, img=cap.read()

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    for face in faces:
        landmarks = predictor(gray, face)

        # Get the coordinates of left and right eyes
        left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
        right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

        # Calculate EAR for both eyes
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)

        # Average EAR
        ear = (left_ear + right_ear) / 2.0


    #to reduce the image size for better recognition
    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
    #to find face in the image and also encode it for comparation
    faceCurFrame=face_recognition.face_locations(imgS)
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img #11
    #imgBackground[218:218+407,97:97+619] = img  # 11
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]#12
    if faceCurFrame:
        #11
        #12
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace) #to show true or false of matching images
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace) #to show distance of the image matching with stored image

            matchIndex=np.argmin(faceDis)

            if ear < EAR_THRESHOLD:
                blink_counter += 1
            elif matches[matchIndex] and blink_counter >= CONSECUTIVE_FRAMES :
                y1,x2,y2,x1=faceLoc
                y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                bbox=55+x1,162+y1,x2-x1,y2-y1
                imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)
                #print('Known Face Detected')
                #print('Student Id:',studentIds[matchIndex])
                id=studentIds[matchIndex]


                if counter ==0:
                    cvzone.putTextRect(imgBackground,"Loading",(320,550))
                    cv2.imshow("Face Attendance",imgBackground)
                    cv2.waitKey(1)
                    counter=1 #this makes update and maked as present
                    modeType=1
                blink_counter=0


        if counter!=0:
            if counter==1:
                #Get the Data
                studentInfo=db.reference(f'Students/{id}').get()
                Present = db.reference(f'Students/Present_Student').get()
                print(studentInfo)
                #Get the Image from the Storage of FireBox
                blob=bucket.get_blob(f'Images/{id}.png')
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #Update data of Attendance of individual & also Date_Time
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds() #to find current time in second format
                print(secondsElapsed)

                if secondsElapsed > 30:  # to remark the attendance
                    # face after 30sec
                    ref=db.reference(f'Students/{id}')
                    #studentInfo['total_attendance'] += 1
                    #ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #update current attendance time to the database
                    #print("Student Id no:",type(id))
                    #StudentId=[]

                    if id not in Present_set:
                        #data wireless transfer
                        try:
                            id_to_send = id
                            # Create a socket connection
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            client_socket.settimeout(5)  # Optional: Set timeout to prevent indefinite waiting
                            client_socket.connect((esp32_ip, esp32_port))
                            # Send the ID
                            client_socket.sendall(id_to_send.encode())
                            print("ID sent to ESP32")
                            # Receive acknowledgment (optional)
                            #ack = client_socket.recv(1024).decode()
                            #print("ESP32 Response:", ack)
                            # Close the socket
                            client_socket.close()
                        except socket.error as e:
                            print(f"Error: Unable to connect or send data to ESP32. {e}")

                        Present_set.add(id)
                        if PresentString:
                            PresentString += f" ,{id}"
                        else:
                            PresentString = str(id)
                        Pref = db.reference(f'Students/Present_Student')
                        Pref.child('Present_List').set(PresentString) #Updating Presented Student
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance']) #Update attendance time
                        #print(type(id))
                        if id in absentList:
                            absentList.remove(id)
                            Aref = db.reference(f'Students/Absentees_Student')
                            Aref.child('Absentees_List').set(absentList)
                        #if id == '4023' or id=='4043' or id=='4056' :
                        filename = f"{id}.mp3"
                        pygame.mixer.music.load(filename)
                        pygame.mixer.music.play()

                    #cv2.waitKey(1)

                    #absentString.removeprefix(id)
                    #Aref = db.reference(f'Students/Absentees_Student')
                    #Aref.child('Absentees_List').set(absentString)
                    #cv2.waitKey(1)
                    #time.sleep(2)

                else:
                    modeType=3
                    counter=0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    cv2.waitKey(1)

            if modeType !=3:

                if 10<counter<20: #to show as Marked
                    modeType=2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                #time.sleep(2)

                if counter <= 10: # to show the Details of the Specific Student
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset=(414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175+216,909:909+216] = imgStudent #to download image of student and showcase in PC
                    #time.sleep(2)
                counter += 1

                if counter>=20: ##to reset the student attendance loop
                    counter=0
                    modeType=0
                    studentInfo=[]
                    imgStudent=[]
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType=0
        counter=0
        #imgBackground[162:162 + 480, 55:55 + 640] = img
        #imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
