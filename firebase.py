import firebase_admin
from firebase_admin import credentials


def init_firebase(project: str):
    cred_obj = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred_obj, {'databaseURL': project})
