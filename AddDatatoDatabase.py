import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


try:
    # Initialize Firebase app with credentials and database URL
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendencerealtime-621a3-default-rtdb.firebaseio.com/"
    })

    # Get a reference to the 'Students' node in the database
    ref = db.reference('Students')

    # Define the data to be pushed to the database
    data = {

        "Shashank": {
            "name": "Shashank Mishra",
            "major": "DSAI",
            "starting_year": 2023,
            "total_attendance": 7,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-04-18 00:44:24" 
        },

         "soham": {
            "name": "Soham Kamble",
            "major": "ECE",
            "starting_year": 2023,
            "total_attendance": 6,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-04-18 00:40:24" 
        },

          "adarsh": {
            "name": "Adarsh Raj",
            "major": "DSAI",
            "starting_year": 2023,
            "total_attendance": 8,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-04-11 10:11:44" 
        },

          "monjulika found": {
            "name": "Vaishnavi Shrivastav",
            "major": "DSAI",
            "starting_year": 2023,
            "total_attendance": 5,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-01-18 00:00:01" 
        },

        "adnan": {
            "name": "MethCookSaul",
            "major": "ECE",
            "starting_year": 2023,
            "total_attendance": 0,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-01-18 00:00:00" 
        },

        "Tanisha": {
            "name": "Tanisha Jain",
            "major": "ECE",
            "starting_year": 2023,
            "total_attendance": 6,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-01-12 12:00:00" 
        },

        "Arnav": {
            "name": "Tanisha Jain",
            "major": "ECE",
            "starting_year": 2023,
            "total_attendance": 6,
            "standing": "G",
            "year": 1,
            "Last_attendance_time": "2024-01-12 12:00:00" 
        },
        
    }

    for key, value in data.items():

        ref.child(key).set(value)

    print("Data successfully added to Firebase Realtime Database!")

except Exception as e:
    print(f"An error occurred: {e}")