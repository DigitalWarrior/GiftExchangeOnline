import smtplib
import string
from google.appengine.api import mail

EMAIL_USERNAME = 'giftshuffle'
DEBUG = True

class EmailFolks(object):

    def format_email(self,giver_receiver):
        """Takes a giver and receiver names as input.
            Formats email parameters for each giver with the name of the person
            they are giving a gift to (receiver)
        """
        host = "localhost"
        subject = "Gift Selection"
        from_address = EMAIL_USERNAME + "@gmail.com"
        to_address = giver_receiver.giver_email
        text = ("Name selections for your gift shuffle. You (%s) are giving presents to %s.") % \
                    (giver_receiver.giver,
                    ','.join(str(r) for r in giver_receiver.receiver))
        if DEBUG: print to_address
        mail.send_mail(sender=from_address,
                    to=to_address,
                    subject=subject,
                    body=text)
