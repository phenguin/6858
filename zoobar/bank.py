from zoodb import *
from debug import *

import time
import auth_client

def transfer(sender, recipient, zoobars, sender_token):

    if sender == recipient:
        raise ValueError("Cannot make transfer to yourself")

    if zoobars <= 0:
        raise ValueError("Transfer amount must be greater than 0")

    if not auth_client.check_token(sender, sender_token):
        raise Exception("Invalid token for user: %s" % (sender,))

    bankdb = bank_setup()
    senderp = bankdb.query(Bank).get(sender)
    recipientp = bankdb.query(Bank).get(recipient)

    sender_balance = senderp.zoobars - zoobars
    recipient_balance = recipientp.zoobars + zoobars

    if sender_balance < 0 or recipient_balance < 0:
        raise ValueError()

    senderp.zoobars = sender_balance
    recipientp.zoobars = recipient_balance
    bankdb.commit()

    transfer = Transfer()
    transfer.sender = sender
    transfer.recipient = recipient
    transfer.amount = zoobars
    transfer.time = time.asctime()

    transferdb = transfer_setup()
    transferdb.add(transfer)
    transferdb.commit()

def balance(username):
    db = bank_setup()
    person = db.query(Bank).get(username)
    return person.zoobars

def init_user_balance(username, initial_balance = 10):
    db = bank_setup()
    entry = Bank()
    entry.username = username
    entry.zoobars = initial_balance
    db.add(entry)
    db.commit()

def get_log(username):
    db = transfer_setup()
    res = []
    qResults = db.query(Transfer).filter(or_(Transfer.sender==username,
                Transfer.recipient==username))

    # Ghetto..
    for t in qResults:
        res.append({
            'time' : t.time,
            'sender' : t.sender,
            'recipient' : t.recipient,
            'amount' : t.amount,
            })

    return res

