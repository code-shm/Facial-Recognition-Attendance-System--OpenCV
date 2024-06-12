import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Initialize Firebase app with credentials and database URL
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendencerealtime-621a3-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendencerealtime-621a3.appspot.com"
})

def upload_image_to_bucket(filename):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        if not blob.exists():
            blob.upload_from_filename(filename)
            print(f"Uploaded {filename} to Firebase Storage")
            return True
        else:
            print(f"{filename} already exists in Firebase Storage")
            return False
    except Exception as e:
        print(f"Error uploading {filename} to Firebase Storage: {e}")
        return False

# Importing the student images
folderPath = 'Images'
PathList = os.listdir(folderPath)
print(PathList)
imgList = []
studentIds = []

for path in PathList:
    student_id = os.path.splitext(path)[0]
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(student_id)

print(studentIds)

for path, student_id in zip(PathList, studentIds):
    if upload_image_to_bucket(f'Images/{path}'):
        print(f"File {path} uploaded successfully.")

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)    
    return encodeList

print("Encoding Started.....  ")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")