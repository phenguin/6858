from zoodb import *
from debug import *

import pbkdf2
import struct
import string
import hashlib
import random
import os

def gen_token(length = 10, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for i in xrange(length))

def token_hash(hashinput):
    return hashlib.md5(hashinput).hexdigest()

def new_salt():
    return struct.unpack("<L", os.urandom(4))[0]


def pw_hash(hashinput, salt):
    log("Salt info:")
    log(type(salt))
    log(salt)
    raw_salt = struct.pack("<L", salt)
    return pbkdf2.PBKDF2(hashinput, raw_salt).read(32)

def cred_for_person(person):
    db = cred_setup()
    return db.query(Cred).get(person.username)

def newtoken(db, cred):
    hashinput = "%s%s" % (cred.username, gen_token(length = 15))
    cred.token = token_hash(hashinput)
    db.commit()
    return hashinput

def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None
    if cred.password == pw_hash(password, cred.salt):
        return newtoken(db, cred)
    else:
        return None

def register(username, password):
    person_db = person_setup()
    cred_db = cred_setup()
    person = person_db.query(Person).get(username)
    cred = cred_db.query(Cred).get(username)
    if person or cred:
        return None

    newperson = Person()
    newperson.username = username
    person_db.add(newperson)

    newcred = Cred()
    salt = new_salt()
    newcred.salt = salt
    newcred.username = username
    newcred.password = pw_hash(password, salt)
    cred_db.add(newcred)

    person_db.commit()
    cred_db.commit()
    return newtoken(cred_db, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token_hash(token):
        return True
    else:
        return False

