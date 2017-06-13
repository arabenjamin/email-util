#!/usr/bin/python
# -*- coding: utf-8 -*-
from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox,\
    Configuration,NTLM,FileAttachment
import os

class mailer(object):
    """ Mailer Class to Send emails via MS Exchange"""

    def __init__(self,cfg,recipient,cc,subject,mybody,attachment=None):
        """ @class parameters:

            #: cfg: credentials to use the exchange account, suplied as a dict
            #: recipient: email address as string
            #: cc: a list of email address strings
            #: ***mybody: the body of the email...
            #: attachment: dict object containing the filename,
            #:             full absolute path of the file to be attached.
            #:             Defaults to None.

        """
        self.config = cfg
        self.recipient = recipient
        self.subject = subject
        self.cc = cc
        self.body = mybody
        self.attachment = attachment

        """ to avoid errors of the Account class, set the smtp_address to string"""
        self.smtp_address = self.config['smtp_address']

        """ setup exchange Credentials, Configuration and Account """
        self.cred = Credentials(username=self.config['username'],\
         password=self.config['password'])
        self.config = Configuration(server = self.config['server'],\
         credentials = self.cred, auth_type=NTLM)
        self.account = Account(primary_smtp_address=self.smtp_address,\
         config=self.config, access_type=DELEGATE)

        """ initialize msg class with our credentials, Configuration and account """
        #: NOTE: every email recipient gets
        #:       suppplied to the msg object with a Mailbox class
        self.msg = Message(
                account=self.account,
                subject=self.subject,
                body=self.body,
                to_recipients=[Mailbox(email_address=self.recipient)],
                cc_recipients =[Mailbox(email_address="dispatch-team@eltec.cc")]
            )

    #check if the eamil is a valid email format
    def isEmailValid(email_address):
        """ Regex is cheap, easy to find, hard to read and verify.But-fuckit.
            This regex is taken from:
            https://github.com/scottbrady91/Python-Email-Verification-Script/blob/master/src/VerifyEmailAddress.py """

        # NOTE: Check out the regex over at
        #       https://github.com/syrusakbary/validate_email/blob/master/validate_email.py
        if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address):
            return False
        return True

    def add_attachment(self):
        """ Add attachment if there's one """
        #: FIXME: fix this shit to always work with any attachment. i.e. Excel/pdfs/word docs/images

        """ self.attachment is a dict, the values, are paths that point to the file to be read"""
        with open(self.attachment['full_path'], 'rb') as f:
            my_attacment = f.read()

        """ create File attachment"""
        self.attachment = FileAttachment(name=self.attachment['name'],\
         content=my_attacment)

        """ attach the file to the msg"""
        return self.msg.attach(self.attachment)

    def sendmsg(self):
        """Attach any included files and the cc list, and send that shit """

        """ check if there's an attachment, attach it if we have it """
        if self.attachment is not None:
            self.add_attachment()

        """ loop through cc list and add them to the msg"""
        for i in self.cc:
            self.msg.cc_recipients.append(Mailbox(email_address=i))
            print "message is being sent to: ",i
            #: TODO: write to logger file who we sent emails to.
            #: TODO: validate the cc_list to be actual emails before loading
            #:      them into the Mailbox class

        """ send the msg and save a copy in exchange """
        return self.msg.send_and_save()


if __name__=='__main__':

    mynotes ="""Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
    nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore eu fugiat
    nulla pariatur. Excepteur sint occaecat cupidatat non proident,
    sunt in culpa qui officia deserunt mollit anim id est laborum."""

    sub = "Ara's Test Email"
    recipient = "asheperdigian@eltec.cc"
    ccList = ["asheperdigian@eltec.cc"]
    #: WAIT!!! You need conf settings first.... this will never work.
    my_mail = mailer(cfg,recipient,ccList,sub,mynotes)
    my_mail.sendmsg()
