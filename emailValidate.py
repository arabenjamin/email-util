#!usr/bin/python
import smtplib
import re

try:
    #Note this library doesn't install correcty everywhere always
    from dns import resolver
except ImportError:
    pass

#Todo: Build class.
fromAddress = 'asheperdigian@eltec.cc'

class EmailError(Exception):
    #Todo: This is lame. pass in the errors and process them.
    pass

class DomianError(Exception):
    #Todo: This is lame. pass in the errors and process them.
    pass


#check if the eamil is a valid email format
def isEmailValid(email_address):
    # Todo: Check out the regex over at https://github.com/syrusakbary/validate_email/blob/master/validate_email.py
	if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address):
		return False
	return True
		
		
#Check to see if the domian exits
def testMx(email_address):
    split = email_address.split('@')
    domain = str(split[1])
    try:
        records = resolver.query(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)  
        return mxRecord		
    except (resolver.NoAnswer,resolver.NXDOMAIN) as error:
        return False

# try and send an email to the address in question.
def aliasTest(mxrecord,email):
    

	# SMTP Conversation
    server = smtplib.SMTP(timeout=10)
    server.set_debuglevel(0)
    server.connect(mxrecord)# What happens if it doesn't connect?
    server.helo(server.local_hostname)
    server.mail(fromAddress)
    code, message = server.rcpt(str(email))
    server.quit()
    #print code 
    #print message

	# Assume SMTP response 250 is success
    if code == 250:
        return True
        # What else though? What if you get status code 550? 
        #Todo: Decide what to do with emails that don't exist at that server. i.e. pull that email from the db?
	return False
 

 
#main Function
def checkUserEmail(email_address):
    #sanitze the input, think wat else should we be looking for.
    email = str(email_address).replace(' ','').replace('u\ax0','').replace('\n','')
    
    match = isEmailValid(email_address)
    if match != True:
	    # ToDo: Kick it back to the user to correct
        raise ValueError('Bad email syntax')
        return False

    domainTest = testMx(email_address)
    if domainTest == False:
        raise DomianError("Either the domain does not exist, or there was no answer from the server")		
        return False

    finalTest = aliasTest(domainTest,email_address)
    if finalTest == False:
        raise EmailError("The alias does not exist at this domain")
        return False
			
    return True




	
if __name__ == "__main__":
    # Lets se how we did...
    emails = ['ara.benjamin@gmail.com',
              'asheperdigian@eltec.cc',
              'dispatch-teamn@eltec.cc',
              'asheperdigian@gmail.com',
              'asshat7@gmail.com',
              'dsfdsfsdfs',
              'shep@sheperdigian.com',
              'ara.benjamin@eltec.cc']

    for email in emails:
		try:
			assert checkUserEmail(email) == True
		except (AssertionError,ValueError,DomianError,EmailError) as e:
			print "Email Address: {0} \nFalied with: {1}\n".format(email,str(e))