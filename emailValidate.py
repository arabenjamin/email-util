#!usr/bin/python
import smtplib
import socket
import re
import time
try:
    #Note/Todo: this library doesn't install correcty everywhere, always
    from dns import resolver
except ImportError:
    pass


fromAddress = 'asheperdigian@eltec.cc'

class InvalidEmailError(ValueError):
	"""Parent class of all exceptions raised by this module."""
	pass

class EmailDeliveryError(Exception):
    '''Alias did not exist at Domain, or we were unable to deliver the email for someother reason. '''
    #Todo: This is lame. pass in the errors and process them.
    pass

class DomianError(Exception):
    '''We were not abale to verify domain of email '''
    #Todo: This is lame. pass in the errors and process them.
    pass

class NetworkError(Exception):
    """something wouldn't connect"""
    pass


#Todo: Put this script into it's own class.	


def server(mxrecord,email):
    # SMTP Conversation
	server = smtplib.SMTP(timeout=2)
	server.set_debuglevel(0)
	server.connect(mxrecord)# What happens if it doesn't connect?
	server.helo(server.local_hostname)
	server.mail(fromAddress)
	code, message = server.rcpt(str(email))
	server.quit()
	time.sleep(1)
	#print code 
	#print message
	return code
	
#check if the eamil is a valid email format
def isEmailValid(email_address):
    """ Regex is cheap, easy to find, hard to read and verify. But fuckit, lets use it. This regex is taken from  https://github.com/scottbrady91/Python-Email-Verification-Script/blob/master/src/VerifyEmailAddress.py """
    # Todo: Check out the regex over at https://github.com/syrusakbary/validate_email/blob/master/validate_email.py
    if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email_address):
        return False
    return True
	
def validate_eAddress_parts(email_address):
    """Lets make sure we're not just taking anything from anybody now, we have rules. Albeit, They may not be the best rules."""
    if not isinstance(email_address,(str, str)):
		try:
			email = email_address.decode("ascii")
		except ValueError:
		    return False
				
    split = email_address.split('@')
    if len(split) !=2:
	    # Make sure there is only on '@' symbol
        return False
    elif len(split[0]) == 0:
	    # Don't allow empty aliases.
		return False
    elif len(split[0]) > 64:
	    # Make sure alias sting is not too long. 
		return False
    
	#Final check, After that wash, lets wash it again. 
    return isEmailValid(email_address)
				
				
		
#Check to see if the domian exits
def recordsTest(email_address):
    split = email_address.split('@')
    domain = str(split[1])
    try:
		records = resolver.query(domain, 'MX')
		mxRecord = records[0].exchange
		mxRecord = str(mxRecord)
		#print "MX:{0} for email:{1} ".format(mxRecord , email_address)
		return mxRecord		
    except (resolver.NoNameservers,resolver.NoAnswer,resolver.NXDOMAIN) as error:
	    # Todo: Test the below. Can you connect to the server with the A/AAAA Records? Do we get the right info there? Someone else did it this way, why can't we?
        try:
            records = resolver.query(domain, 'A')
            ARecord = [(0, str(r)) for r in records]
            ARecord = str(ARecord)
            #print "A:{0} for email:{1} ".format(ARecord , email_address)
            return ARecord			
        except(resolver.NoNameservers,resolver.NoAnswer,resolver.NXDOMAIN) as error:
            try:
                records = resolver.query(domain, 'AAAA')
                AAAARecord = [(0, str(r)) for r in records]
                AAAARecord = str(AAAARecord)
                #print "AAAA :{0} for email:{1} ".format(ARecord , email_address)
                return AAAARecord				
            except(resolver.NoNameservers,resolver.NoAnswer,resolver.NXDOMAIN) as error:
                return False

# try and send an email to the address in question.
def aliasTest(mxrecord,email):
    # Will this method work with A & AAAA records?
    try:
		# SMTP Conversation
		code = server(mxrecord,email)
    except smtplib.SMTPServerDisconnected:
        try:
            code = server(mxrecord,email)		
        except Exception as e:
            print e		
		
    except (socket.error,socket.timeout):
        raise NetworkError('Falied to connect to mail server, Either timeout or someother error') 
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
    
    match = validate_eAddress_parts(email_address)
    if match != True:
	    # ToDo: Kick it back to the user to correct
        raise InvalidEmailError('Bad email syntax')
        return False

    domainTest = recordsTest(email_address)
    if domainTest == False:
        raise DomianError("Either the domain does not exist, or there was no answer from the server")		
        return False

    try:
        finalTest = aliasTest(domainTest,email_address)
        
    except NetworkError:
        raise NetworkError('Falied to connect to mail server, Either timeout or someother error')
        return False
		
    if finalTest == False:
		raise EmailDeliveryError("Could not reach alias at this domian")
		return False

	
    return True




	
if __name__ == "__main__":
    # Lets se how we did...
    emails = ['ara.benjamin@gmail.com',
              'asheperdigian@eltec.cc',
              'dispatch-team@eltec.cc',
              'asheperdigian@gmail.com',
              'asshat7@gmail.com',
              'dsfdsfsdfs',
              'shep@sheperdigian.com',
              'ara.benjamin@eltec.cc',
              'hhpeterson@evergreenhealthcare.org',
              'DITotaan@evergreenhealthcare.org']

    for email in emails:
        try:
            assert checkUserEmail(email) == True
			#now send them an email
            print "\nEmail Address: {0} Passed".format(email)
        except (AssertionError,ValueError,DomianError,EmailDeliveryError,InvalidEmailError,NetworkError) as e:
			print "\nEmail Address: {0} \nFalied with: {1}\n".format(email,str(e))