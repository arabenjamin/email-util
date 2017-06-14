#!usr/bin/python
# -*- coding: utf-8 -*-

from mailer import mailer
import json

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


    my_mail = mailer(cfg['exchange'],recipient,ccList,sub,mynotes)
    my_mail.sendmsg()
