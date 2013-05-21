#!/usr/bin/env python

import sys
import string
import os
import urllib
import time
import webapp2
import datetime
import jinja2
from single_selector import ChristmasNamesSelector # as name_selector
from single_selector import GiverReceiverPair
from google.appengine.ext import ndb
from constants import DEBUG, last_name

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

'''def group_key(group_name=None):
    """Constructs a Datastore key for a Group entity with group_name"""
    return ndb.Key("Group", group_name or "default")
'''

class EntryPage(webapp2.RequestHandler):

    def get(self):
        possible = string.lowercase + string.digits
#starting page - a form to enter names
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
            if self.request.get(name) is not u'':
                if DEBUG: print(self.request.get(name), self.request.get(email))
                name_list.append((self.request.get(name), self.request.get(email)))
#there has to be a better way to get a list of items from a web form

        name_selector = ChristmasNamesSelector(name_list, 1)
        matches = name_selector.pair_names()
        name_selector.print_pairs(matches)

#add to Datastore
        #this creates the object and sets its ancestor
        for match in matches:
            for r in match.receiver:
                pair = GiverReceiver(giver=match.giver,
                                     receiver=r.encode('utf8'),
                                     email=match.giver_email,
                                     group=group_name)
                pair.put()
        time.sleep(.2) #give the database time to insert and show entries.
#Surely there's a better way?

        query_params = {'group_name': group_name}
        self.redirect('/display?' + urllib.urlencode(query_params))

#TODO: email


class Display(webapp2.RequestHandler):

    def get(self):
        group_name = self.request.get('group_name')
        if DEBUG: print 'group_name from display is', group_name
        pairs_query = GiverReceiver.query(GiverReceiver.group == group_name)
        pairs = pairs_query.fetch(10)
#if add a login section, could have items grouped by parent as 
# person logged in and session/group

        template_values = {
                'pairs': pairs,
                'group_name': group_name,
        }

        template = JINJA_ENVIRONMENT.get_template('templates/display.html')
        self.response.write(template.render(template_values))

#look into template inheritance in jinja2

app = webapp2.WSGIApplication([('/', EntryPage),
                                ('/assigned', Results),
                                ('/display', Display)],
                                debug=True)
