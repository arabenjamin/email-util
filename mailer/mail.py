#!/usr/bin/python
# -*- coding: utf-8 -*-
from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox,\
    Configuration, NTLM
from exchangelib import FileAttachment
import logging
import sys,os,re


""" Class Errors """
class InvalidEmailError(ValueError):
    pass

class InvalidConfigObject(ValueError):
    pass

class InvalidRecipient(ValueError):
    pass

class InvalidAttachment(ValueError):
    pass

class mailer(object):
    """ Mailer Class to Send emails via MS Exchange"""

    def __init__(self,cfg):

        """ Init class and validate cfg object """
        logging.info("Mailer Initiated ")
        self.config = cfg
        if not isinstance(self.config,dict):
            raise InvalidConfigObject("cfg parameter is not a dict object")

        """ to avoid errors from the Account class, set the smtp_address to string """
        self.smtp_address = str(self.config['smtp_address'])

        """ setup exchange Credentials, Configuration and Account """
        self.cred = Credentials(username=str(self.config['username']),\
         password=str(self.config['password']))

        self.config = Configuration(server = str(self.config['server']),\
         credentials = self.cred, auth_type=NTLM)

        self.account = Account(primary_smtp_address=self.smtp_address,\
         config=self.config, access_type=DELEGATE)

        """ set message object """
        self.msg = Message(account=self.account)


    """ Validate email string; return True if valid, False for otherwise"""
    def isEmailValid(self,email_address):

        if not isinstance(email_address, (basestring, str, unicode)):
             logging.info("{} is not an email address".format(email_address))
             return False

        email_address = email_address.lower().replace(" ","")

        # NOTE: Regex is cheap, easy to find, hard to read and verify. But-fuckit.
        #       Check out the regex over at
        #       https://github.com/syrusakbary/validate_email/blob/master/validate_email.py
        #
        #       This regex is taken from:
        #       https://github.com/scottbrady91/Python-Email-Verification-Script/blob/master/src/VerifyEmailAddress.py

        if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,63})$', email_address):
            logging.info("{} is not an email address".format(email_address))
            return False
        return True

    def add_attachment(self):
        """ Add attachment if there's one """

        #: FIXME: fix this shit to always work with any attachment. i.e. Excel/pdfs/word docs/images
        for i in self.attachment:

            """ self.attachment is a dict, the values, are paths that point to the file to be read"""
            with open(i['full_path'], 'rb') as f:
                my_attacment = f.read()

            """ create File attachment"""
            this_attachment = FileAttachment(name=i['name'],\
            content=my_attacment)

            """ attach the file to the msg"""
            self.msg.attach(this_attachment)
        return

    def sendmsg(self, recipient,  subject, cc=None, mybody=None, attachment=None):
        logging.info("Sending email to {}".format(recipient))
        """ #: @method parameters:
            #: @recipient   : email address as string
            #: @cc          : a list of email address strings
            #: @mybody***   : the body of the email...
            #: @attachment  : dict object containing the filename,
            #:                full absolute path of the file to be attached.
            #:                Defaults to None.
        """

        """ Validate parameters """
        self.subject = subject
        self.body = mybody
        self.attachment = attachment
        self.recipient = recipient
        self.cc = cc

        """ validate email address before initializeing the Message class """
        if self.isEmailValid(self.recipient) != True:
            raise InvalidEmailError("Refusing to send email to address {0} : invalid email address format ".format(self.recipient))

        self.msg.to_recipients = [Mailbox(email_address=self.recipient)]
        self.msg.subject = self.subject
        if self.body is not None:
            #TODO: Validate msg bady to be of only a couple of types
            self.msg.body = self.body

        """Attach any included files and the cc list, and send that shit """

        """ check if there's an attachment, attach it if we have it """
        if self.attachment is not None:
            if not isinstance(self.attachment, list):
                logging.error("ATTACHMENT ERROR: The attachment needs to be a list of dictionary objects")
                raise InvalidAttachment("The attachment needs to be a list of dictionary objects")
            self.add_attachment()

        """ validate cc list"""
        if self.cc is not None:
            self.msg.cc_recipients = []

            if not isinstance(self.cc,(list,tuple)):
                logging.error("CC LIST ERROR: CC list must be a list or tupple")
                raise InvalidRecipient("CC list must be a list or tupple")

            for cc in self.cc:
                if self.isEmailValid(cc) is True:
                    """ if it's valid add it to the list """
                    if cc not in self.msg.cc_recipients:
                        self.msg.cc_recipients.append(Mailbox(email_address=cc))
                        log_info = "message is being sent to: {0} as: {1} ".format(cc, self.smtp_address)
                        logging.info(log_info)
                else:
                    #raise InvalidEmailError("Refusing to send email to address {0} : invalid email address format, ".format(cc))
                    #: TODO: write to logger file who we did not send emails to.
                    log_info = "Refusing to send email to address {0}: Invalid email address format".format(cc)
                    logging.info(log_info)

        """ send the msg and save a copy in exchange """
        return self.msg.send_and_save()
