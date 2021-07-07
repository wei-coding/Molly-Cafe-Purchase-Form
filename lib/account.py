import json
import hashlib
from enum import Enum, auto
import re

salt = 'wfgyiqfi47hh'

class Hint(Enum):
    InvalidTelephoneNumber = auto()
    InvalidUsernameOrPassword = auto()
    UsernameIsExisted = auto()
    SignupSuccess = auto()
    LoginSuccess = auto()

def login_check(username, password):
    # open database first
    database = json.load(open('lib/db.json', 'r'))
    # search username from json file
    user_with_salt = username + salt
    id = hashlib.sha256(user_with_salt.encode('utf-8')).hexdigest()
    pw_from_db = database.get(id)['pwd']
    # check if existed
    if pw_from_db is None:
        return Hint.InvalidUsernameOrPassword, None
    else:
        # check if password corrected
        pwd_with_salt = password + salt
        if hashlib.sha256(pwd_with_salt.encode('ascii', 'ignore')).hexdigest() == pw_from_db:
            return Hint.LoginSuccess, id
        else:
            return Hint.InvalidUsernameOrPassword, None

def check_admin(id):
    # open database first
    database = json.load(open('lib/db.json', 'r'))
    # search id from json file
    info = database.get(id)
    if info is None:
        return Hint.InvalidUsernameOrPassword
    elif info.get('type') == 'admin':
        return Hint.LoginSuccess
    else:
        return Hint.InvalidUsernameOrPassword

def signup(username, password) -> Hint :
    # open database first
    database = json.load(open('lib/db.json', 'r'))
    # search username from json file 
    user_with_salt = username + salt
    pw_from_db = database.get(hashlib.sha256(user_with_salt.encode('utf-8')).hexdigest())
    # check if not existed
    if pw_from_db:
        return Hint.UsernameIsExisted
    else:
        pwd_with_salt = password + salt
        database[hashlib.sha256(user_with_salt.encode('utf-8')).hexdigest()] = {
            'type': 'admin',
            'name': username,
            'pwd': hashlib.sha256(pwd_with_salt.encode('ascii', 'ignore')).hexdigest(),
        }
    json.dump(database, open('lib/db.json', 'w'))
    return Hint.SignupSuccess

class Status(Enum):
    SignInSuccess = auto()
    SignUpSuccess = auto()
    InvalidTelephoneNumber = auto()

def customer(user, telephone):
    database = json.load(open('lib/db.json', 'r'))
    if re.match('^09\d{8}$', telephone) is None:
        return Status.InvalidTelephoneNumber, None
    user_hash = hashlib.sha256(user.encode('utf-8')).hexdigest()
    if database.get(user_hash) is None:
        database[user_hash] = {
            'type': 'customer',
            'name': user,
            'telephone': telephone,
            'purchase_record': []
        }
        json.dump(database, open('lib/db.json', 'w'))
        return Status.SignUpSuccess, user_hash
    else:
        return Status.SignInSuccess, user_hash

def search_name(user_hash):
    database = json.load(open('lib/db.json', 'r'))
    return database.get(user_hash)['name']

def search_data(user_hash):
    database = json.load(open('lib/db.json', 'r'))
    return database.get(user_hash)

def customer_order(user_hash, order):
    database = json.load(open('lib/db.json', 'r'))
    try:
        database.get(user_hash)['purchase_record'][order['items']] = order['num-items']
    except IndexError:
        database.get(user_hash)['purchase_record'].insert(order['items'], order['num-items'])
    json.dump(database, open('lib/db.json', 'w'))

def reset_all_order():
    database = json.load(open('lib/db.json', 'r'))
    for k, v in database.items():
        if v.get('purchase_record'):
            v['purchase_record'] = []
    json.dump(database, open('lib/db.json', 'w'))

def get_all_customer_data():
    database = json.load(open('lib/db.json', 'r'))
    data = []
    for k, v in database.items():
        if v.get('type') == 'customer':
            data.append({
                'name': v['name'],
                'telephone': v['telephone'],
                'purchase_record' : v['purchase_record']
            })
    return data

if __name__ == "__main__":
    print(signup('cynthia', 'cynthia-1103'))