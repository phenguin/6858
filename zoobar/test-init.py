#!python

import auth
import bank

auth.register("alice", "alice")
auth.register("bob", "bob")
bank.init_user_balance("alice")
bank.init_user_balance("bob")
