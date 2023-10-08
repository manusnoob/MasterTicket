import firebase_admin as fb
from firebase_admin import credentials, db

# from vd_TEST import verification_dict as TEST
# from vd_NOON import verification_dict as NOON
# from vd_NIGHT import verification_dict as NIGHT

# init = {**TEST, **NOON, **NIGHT}


def firebase_init():
    cred = credentials.Certificate("serviceAccountKey.json")
    fb.initialize_app(cred, {
        "databaseURL": "https://mastercode-c652f-default-rtdb.firebaseio.com/"
    })


def save(path, json):
    ref = db.reference(path)
    ref.set(json)

def update(path, obj, json):
    ref = db.reference(path)
    child_ref = ref.child(obj)
    child_ref.update(json)

def read(path):
    data =  db.reference(path).get()
    return data

def delete(path, obj):
    ref = db.reference(path)
    child_ref = ref.child(obj)
    child_ref.delete()

# example
if __name__ == '__main__':
    firebase_init()
    save("/SKHTST_DRAMA_QRCODE", {})
