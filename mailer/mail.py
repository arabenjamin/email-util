#!/usr/bin/python
# -*- coding: utf-8 -*-
from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox,\
    Configuration, NTLM
from exchangelib import FileAttachment
import sys,os,re

class InvalidEmailError(ValueError):
	"""Parent class of all exceptions raised by this module."""
	pass

class mailer(object):
    """ Mailer Class to Send emails via MS Exchange"""

    def __init__(self,cfg,recipient,cc,subject,mybody,attachment=None):
        """ @class parameters:

            #: @cfg: credentials for the exchange account, suplied as a dict
            #: @recipient   : email address as string
            #: @cc          : a list of email address strings
            #: @mybody***   : the body of the email...
            #: @attachment  : dict object containing the filename,
            #:                full absolute path of the file to be attached.
            #:                Defaults to None.

        """
        self.config = cfg
        self.recipient = recipient
        self.subject = subject
        self.cc = cc
        self.body = mybody
        self.attachment = attachment

        """ to avoid errors from the Account class, set the smtp_address to string """
        self.smtp_address = self.config['smtp_address']

        """ setup exchange Credentials, Configuration and Account """
        self.cred = Credentials(username=self.config['username'],\
         password=self.config['password'])
        self.config = Configuration(server = self.config['server'],\
         credentials = self.cred, auth_type=NTLM)
        self.account = Account(primary_smtp_address=self.smtp_address,\
         config=self.config, access_type=DELEGATE)

        """ validate email address before initializeing the Message class"""
        if self.isEmailValid(self.recipient) != True:
            raise InvalidEmailError("Refusing to send email to address {0} : invalid email address format ".format(self.recipient))
            #sys.exit()


        """ initialize msg class with our credentials, Configuration and account """
        #: NOTE: every email recipient gets
        #:       suppplied to the msg object with a Mailbox class
        self.msg = Message(
                account=self.account,
                subject=self.subject,
                body=self.body,
                to_recipients=[Mailbox(email_address=self.recipient)],
                cc_recipients =[]
            )

    #check if the eamil is a valid email format
    def isEmailValid(self,email_address):
        """ Regex is cheap, easy to find, hard to read and verify.But-fuckit.
            This regex is taken from:
            https://github.com/scottbrady91/Python-Email-Verification-Script/blob/master/src/VerifyEmailAddress.py """


        # NOTE: Check out the regex over at
        #       https://github.com/syrusakbary/validate_email/blob/master/validate_email.py

        email_address = email_address.lower().replace(" ","")
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

            """ valifdate the email that we're sending to"""
            if self.isEmailValid(i) is True:

                if i not in self.msg.cc_recipients:

                    self.msg.cc_recipients.append(Mailbox(email_address=i))
                    print "message is being sent to: {0} as: {1} ".format(i,self.smtp_address)
                    #: TODO: write to logger file who we sent emails to.
            else:
                raise InvalidEmailError("Refusing to send email to address {0} : invalid email address format, ".format(i))
                #: TODO: write to logger file who we did not send emails to.

        """ send the msg and save a copy in exchange """
        return self.msg.send_and_save()
