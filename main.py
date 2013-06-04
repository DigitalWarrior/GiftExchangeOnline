#!/usr/bin/env python 
import sys
import re
import string
import os
import urllib
import time
import webapp2
import jinja2
from google.appengine.ext import ndb
from emailer import EmailFolks, EMAIL_USERNAME, DEBUG
from single_selector import ChristmasNamesSelector

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'])
DEBUG = True

class GiverReceiver(ndb.Model):
    '''Models an individual giver:receiver pair entry to the db'''
    giver = ndb.StringProperty()
    receiver = ndb.StringProperty()  # note: single receiver (for now)
    email = ndb.StringProperty()
    group = ndb.StringProperty()


class EntryPage(webapp2.RequestHandler):

    def write_form(self, template_values):
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))

    def get(self):
        possible = string.lowercase + string.digits
        my_id = ndb.Key(GiverReceiver, 1)
        F, _ = GiverReceiver.allocate_ids(1)
        group_name = str(F)
        if DEBUG:
            print 'group name from EntryPage is', group_name
            print 'type of group name is',type(group_name)
        template_values = {
                'errors': '',
        }
                #'group_name': group_name,
                #'query_params': urllib.urlencode({'group_name':group_name.encode('utf8')}),
        self.write_form(template_values)

    def post(self):
        name_list = []
        title = self.request.get("title")
        for i in range(1,11):
            name = "name"+str(i)
            email = "email"+str(i)
            #if name is not u'' and email is u'':
                #give an error about filling in email and go back
                #pass
            if self.request.get(name) is not u'':
                if DEBUG: print(self.request.get(name), self.request.get(email))
                name_list.append((self.request.get(name), self.request.get(email)))

        if DEBUG: print 'made it to post'
        group_name = self.request.get('group_name')
        if DEBUG: print 'group name is ', group_name

        errors = self.validate(name_list)
        if errors != '':
            errors += "Please try again."
            if DEBUG: print 'errors present: ',errors
        #TODO: finish below
            template_values = {
                    'errors': errors,
            } #finish
            self.write_form(template_values)
        else:
            name_selector = ChristmasNamesSelector(name_list, 1)
            matches = name_selector.pair_names()
            if DEBUG: name_selector.print_pairs(matches)
            emailer = EmailFolks()
            for match in matches:
                emailer.format_email(match)

            self.redirect('/thanks')

    def validate(self, name_list):
        names = [x[0] for x in name_list]
        errors = ''
        email_regex = re.compile(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")
        if len(names) != len(set(names)):
            errors += "No duplicate names allowed.\n\n"
        for x in name_list:
            if x[1] == u'':
                errors += "Every name must have an associated email.\n\n"
            else:
                if not email_regex.match(x[1]):
                    errors += "Please enter a valid email. You entered %s.\n" % (x[1])
        if DEBUG: print errors
        return errors
#check email format
#verify no duplicate names
#all names have emails


class Thanks(webapp2.RequestHandler):

    def get(self):
        template_values = {
                'email': EMAIL_USERNAME + "@gmail.com",
        }
        template = JINJA_ENVIRONMENT.get_template('templates/thanks.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', EntryPage),
                                ('/thanks', Thanks)],
                                debug=True)
