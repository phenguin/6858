#!/usr/bin/python
#
# Insert bank server code here.
#

#!/usr/bin/python

import rpclib
import sys
import auth
import bank
from debug import *

class BankRpcServer(rpclib.RpcServer):
    def rpc_transfer(self, sender, recipient, zoobars, sender_token):
        return bank.transfer(sender, recipient, zoobars, sender_token)

    def rpc_balance(self, username):
        return bank.balance(username)

    def rpc_init_user_balance(self, username):
        return bank.init_user_balance(username)

    def rpc_get_log(self, username):
        res = bank.get_log(username)
        log(type(res))
        log(res)
        return res

(_, dummy_zookld_fd, sockpath) = sys.argv

s = BankRpcServer()
s.run_sockpath_fork(sockpath)
