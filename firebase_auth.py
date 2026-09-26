import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDe7AwQ77xL3Z4rj19wfp2h_CLEyQrO1YI",
    "authDomain": "eduhub-3852.firebaseapp.com",
    "projectId": "eduhub-3852",
    "storageBucket": "eduhub-3852.appspot.com",
    "messagingSenderId": "333263717092",
    "appId": "1:333263717092:web:e353a50f58d0f8137aa2f1",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()