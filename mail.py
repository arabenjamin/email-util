#!/usr/bin/python

from exchangelib import DELEGATE, Account, Credentials, Message, Mailbox,Configuration,NTLM

class mailer(object):
    
    def __init__(self,recipient,cc,subject,mybody):
        self.recipient = recipient
        self.subject = subject
        self.cc = cc
        self.body = mybody  
        self.cred = Credentials(username='eltec\\dispatch-team', password='clanT7665^^')
        self.config = Configuration(server = 'mail.eltec.cc', credentials = self.cred, auth_type=NTLM)
        self.account = Account(
                primary_smtp_address='dispatch-team@eltec.cc', config=self.config, access_type=DELEGATE)
        self.msg = Message(
                account=self.account,
                subject=self.subject,
                body=self.body,
                to_recipients=[Mailbox(email_address=self.recipient)],
                cc_recipients =[Mailbox(email_address="dispatch-team@eltec.cc")] 
            )
    def sendmsg(self):	
        for i in self.cc:
            self.msg.cc_recipients.append(Mailbox(email_address=i))
            print i
            print "message sent"
        return self.msg.send_and_save()

    
    
if __name__=='__main__':
    
    sub = "Ara's Test PLace"
    mymsg = "This is a test !\nIf this email reaches it's recipient, then the test was sucessful."
    ccList = ["asheperdigian@eltec.cc"]
    x = mailer("ara.benjamin@gmail.com",ccList,sub,mymsg)
    x.sendmsg()
