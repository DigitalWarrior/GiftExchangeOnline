#!/usr/bin/env python

import sys
import os
import urllib
import webapp2
import datetime
import jinja2
from single_selector import ChristmasNamesSelector # as name_selector
from single_selector import GiverReceiverPair
from google.appengine.ext import db
from constants import address_list, address_list_test, DEBUG, last_name

glob_counter = 0 #take this out once have a more sophisticated way of setting parent
JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class GiverReceiver(db.Model):
    '''Models an individual giver:receiver pair entry to the db'''
    giver = db.StringProperty()
    receiver = db.StringProperty()  # note: single receiver (for now)

def group_key(group_name=None):
    """Constructs a Datastore key for a Group entity with group_name"""
    return db.Key.from_path("Group", group_name or "default")
#default? or force a name?

class EntryPage(webapp2.RequestHandler):

    def get(self):
        global glob_counter
#starting page - a form to enter names
        group_name = glob_counter
        glob_counter += 1

        template_values = {
                'group_name': group_name,
        }

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))


class Results(webapp2.RequestHandler):

    def post(self):
        print 'made it to Results'
        group_name = self.request.get('group_name')
        print 'group name is ', group_name
        name_list = []
        for i in range(1,11):
            print self.request.get(str(i))
            name_list.append(self.request.get(str(i)))
#there has to be a better way to get a list of items from a web form

        #name_list = address_list.keys()  #get these from webpage
        name_selector = ChristmasNamesSelector(name_list, 1)
        matches = name_selector.pair_names()
        name_selector.print_pairs(matches)

#add to Datastore
        #this creates the object and sets its ancestor
        for match in matches:
            for r in match.receiver:
                pair = GiverReceiver(parent=group_key(group_name))
                pair.giver = match.giver
                pair.receiver = r
#probably a better way to do the above -- can the GR's be the same class?
                pair.put()

        query_params = {'group_name': group_name}
        self.redirect('/display')#?' + urllib.urlencode(query_params))#?' + urllib.urlencode(query_params))
    #for each pair in matches, create a new database entry with the
    # same ancestor. Then can pull these out to populate the page(?)

#TODO: email


class Display(webapp2.RequestHandler):

    def get(self):
        group_name = self.request.get('group_name')
        print 'group_name from display is', group_name
#need to assign a group name but not have user define it (unless they
# want to?) to keep giver/receivers together in the same entity.
#Can provide this group name (or a hashed version?) back to the
# user for re-lookup if they lose results? Maybe worry about this 
# part later
        pairs_query = GiverReceiver.all().ancestor(
                group_key(group_name))
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
