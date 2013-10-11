from debug import *
from zoodb import *
import rpclib

def transfer(sender, recipient, zoobars):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('transfer', sender = sender, recipient = recipient, zoobars = zoobars)

def balance(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('balance', username=username)

def init_user_balance(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        return c.call('init_user_balance', username=username)

def get_log(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        return iter(c.call('get_log', username=username))

