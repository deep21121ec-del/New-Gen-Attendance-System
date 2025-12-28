import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-b690f-default-rtdb.firebaseio.com/",
    'storageBucket':"attendance-system-b690f.appspot.com"
})

#Importing Student images
folderPath='Images'
PathList=os.listdir(folderPath)
imgList=[]
studentIds=[]
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName=f'{folderPath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName) #uploading images to firebase

    #print(path)
    #print(os.path.splitext(path)[0])
    print(studentIds)

def findEncodings(imagesList):
    encodeList=[]
    for img in imagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started....")
encodeListKnow=findEncodings(imgList)
encodeListKnowWithIds=[encodeListKnow,studentIds]
print("Encode Completed")

file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnowWithIds,file)
file.close()
print("File Saved")

