#!/usr/bin/env python

# kwidman
# 12/1/11 updated April 24, 2013
# Christmas name selector

import random
from google.appengine.ext import db
from constants import DEBUG

class GiverReceiverPair(object):
    '''Class to hold a pair of giver and receiver.
        Note that receiver can be a list of receivers.
    '''
    def __init__(self, giver, receiver):
        self.giver = giver
        self.receiver = receiver

    def __repr__(self):
        return self.giver + repr(self.receiver)


class ChristmasNamesSelector(object):
    '''Methods associated with pairing givers and receivers randomly.
        Contains two public methods for pairing names when given a list
        and to print the pairs.  Also contains private method(s)
    '''

    def __init__(self, name_list, number_receivers):
        self.name_list = name_list
        self.number_receivers = number_receivers

    def _select_names(self, giver, receiver_list):
        '''Given one name (giver) and a list of receivers (all not
            yet paired), selects a receiver from the list and creates
            a GiverReceiverPair object.  Returns said object. 
        '''
        receivers = list(receiver_list)
        receiver_picks = []
        for i in range(self.number_receivers):
            receiver = random.choice(receivers)
            receivers.remove(receiver)
            receiver_picks.append(receiver)
        if (giver not in receiver_picks): #giver cannot be same as receiver
            giver_receiver_match = GiverReceiverPair(giver, receiver_picks)
            return giver_receiver_match
        else:
            return self._select_names(giver, receiver_list)

    def pair_names(self):
        '''Main functionality - takes a list of names and returns
            a list of GiverReceiverPair objects. If only name left
            in receiver_list is == giver, this method sets the list
            to empty and calls itself again.
        '''
        giver_list = list(self.name_list)
        receiver_dict = {}
        list_of_giver_receivers = []
        for receiver in self.name_list:
            receiver_dict[receiver] = 0
        for name in giver_list:
            if ((len(receiver_dict) > self.number_receivers) or (len(receiver_dict) == self.number_receivers and name not in receiver_dict)):
                giver_receiver = self._select_names(name, receiver_dict.keys())
                for receiver in giver_receiver.receiver:
                    receiver_dict[receiver] += 1
                    if receiver_dict[receiver] >= self.number_receivers:
                        del receiver_dict[receiver]
                list_of_giver_receivers.append(giver_receiver)
            else:
                return self.pair_names()
        return list_of_giver_receivers

    def print_pairs(self, giver_receiver_pairs):
        '''Method to print the generated giver/receiver pairs.
            Takes a GiverReceiverPair object as input.
            Returns nothing.
        '''
        for pair in giver_receiver_pairs:
            print pair.giver + " : " + repr(pair.receiver) + '\n'
        return
