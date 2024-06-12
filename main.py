import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

class FaceAttendanceSystem:
    def _init_(self, service_account_key_path):
        self.initialize_firebase(service_account_key_path)
        self.load_encoding_file()
        self.init_capture()
        

    def initialize_firebase(self, service_account_key_path):
        cred = credentials.Certificate(service_account_key_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://faceattendencerealtime-621a3-default-rtdb.firebaseio.com/",
            'storageBucket': "faceattendencerealtime-621a3.appspot.com"
        })
        self.bucket = storage.bucket()
        print("Firebase initialized successfully.")

    def load_encoding_file(self):
        with open('EncodeFile.p', 'rb') as file:
            self.encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.studentIds = self.encodeListKnownWithIds

    def init_capture(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def run(self):
        imgBackground = cv2.imread('Resources/background.png')
        folderModePath = 'Resources/Modes'
        modePathList = os.listdir(folderModePath)
        imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]
        for path in modePathList:
            imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

        resize_factor = 0.25
        modeType = 0
        counter = 0
        id = -1
        imgStudent = []
        studentInfo = None

        while True:
            success, img = self.cap.read()
            imgS = cv2.resize(img, (0, 0), None, resize_factor, resize_factor)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            faceCurrentFrame = face_recognition.face_locations(imgS)
            encodeCurrentFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)
            imgBackground[162:162+480, 55:55+640] = img

            if faceCurrentFrame:
                for encodeFace, faceLoc in zip(encodeCurrentFrame, faceCurrentFrame):
                    matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                        id = self.studentIds[matchIndex]
                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                            cv2.imshow("Face Attendance", imgBackground)
                            cv2.waitKey(1)
                            counter = 1
                            modeType = 1

                if counter != 0:
                    if counter == 1:
                        studentInfo = db.reference(f'Students/{id}').get()
                        blob = self.bucket.get_blob(f'Images/{id}.jpeg')
                        if blob is not None:
                            array = np.frombuffer(blob.download_as_string(), np.uint8)
                            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                        imgStudent = cv2.resize(imgStudent, (216, 216))
                        datetimeObject = datetime.strptime(studentInfo['Last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        print(secondsElapsed)
                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('Last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            modeType = 3
                            counter = 0
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if modeType != 3:
                        if 10 < counter < 20:
                            modeType = 2
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                        if counter <= 10:
                            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
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
                            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
                        counter += 1
                        if counter >= 20:
                            counter = 0
                            modeType = 0
                            studentInfo = []
                            imgStudent = []
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            else:
                modeType = 0
                counter = 0

            cv2.imshow("Face Attendance", imgBackground)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

# Initialize the system
service_account_key_path = "serviceAccountKey.json"
attendance_system = FaceAttendanceSystem(service_account_key_path)
# Run the system
attendance_system.run()