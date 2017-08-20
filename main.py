#!usr/bin/python
# -*- coding: utf-8 -*-

from mailer import mailer, InvalidEmailError
import sys, json



if __name__ == '__main__':

    json_data_file = open('config.json')
    cfg = json.load(json_data_file)

    recipient = "asheperdigian@eltec.cc"
    ccList = ["asheperdigian@eltec.cc"]
    sub = "Ara's Test Email"

    mynotes ="""Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat
nulla pariatur. Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum."""

    if len(sys.argv) == 2:
        recipient = str(sys.argv[1])
    try:
        my_mail = mailer(cfg['exchange'])
        my_mail.sendmsg(recipient, sub, cc=ccList, mybody=mynotes)
    except InvalidEmailError:
        print "{0} is an invalid Email address".format(sys.argv[1])
