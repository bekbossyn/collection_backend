import os
#TODO setup for collection_backend
import pyrebase
from django.conf import settings

config = {
    "apiKey": "AIzaSyBB8mhUthsygk49WuwVMmhevJ8kMFIuCVI",
    "authDomain": "belka-firebase.firebaseapp.com",
    "databaseURL": "https://belka-firebase.firebaseio.com",
    # "projectId": "belka-firebase",
    "storageBucket": "belka-firebase.appspot.com",
    # "messagingSenderId": "787501788521",
    "serviceAccount": os.path.join(settings.BASE_DIR, 'firebase.json'),
  }

firebase = pyrebase.initialize_app(config)
