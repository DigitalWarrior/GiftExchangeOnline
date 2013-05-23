#!/usr/bin/env python 
import sys
import string
import os
import urllib
import time
import webapp2
import jinja2
from google.appengine.ext import ndb
from constants import DEBUG, email_username
from emailer import EmailFolks
from single_selector import ChristmasNamesSelector # as name_selector
from single_selector import GiverReceiverPair

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

    def get(self):
        possible = string.lowercase + string.digits
        my_id = ndb.Key(GiverReceiver, 1)
        F, _ = GiverReceiver.allocate_ids(1)
        group_name = str(F)
        if DEBUG:
            print 'group name from EntryPage is', group_name
            print 'type of group name is',type(group_name)
        template_values = {
                'group_name': group_name,
                'query_params': urllib.urlencode({'group_name':group_name.encode('utf8')}),
        }
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))


class Results(webapp2.RequestHandler):

    def post(self):
        if DEBUG: print 'made it to Results'
        group_name = self.request.get('group_name')
        if DEBUG: print 'group name is ', group_name
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

        name_selector = ChristmasNamesSelector(name_list, 1)
        matches = name_selector.pair_names()
        if DEBUG: name_selector.print_pairs(matches)
        emailer = EmailFolks()
        for match in matches:
            emailer.format_email(match)

        self.redirect('/thanks')


class Thanks(webapp2.RequestHandler):

    def get(self):
        template_values = {
                'email': email_username + "@gmail.com",
        }
        template = JINJA_ENVIRONMENT.get_template('templates/thanks.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', EntryPage),
                                ('/assigned', Results),
                                ('/thanks', Thanks)],
                                debug=True)
