#!/usr/bin/env python

# kwidman
# 12/1/11 updated April 24, 2013
# Christmas name selector

import random
from emailer import DEBUG

class GiverReceiverPair(object):
    '''Class to hold a pair of giver and receiver.
        Note that receiver can be a list of receivers.
    '''
    def __init__(self, giver, receiver, giver_email):
        self.giver = giver
        self.receiver = receiver
        self.giver_email = giver_email

    def __repr__(self):
        return self.giver + repr(self.receiver)


class ChristmasNamesSelector(object):
    '''Methods associated with pairing givers and receivers randomly.
        Contains two public methods for pairing names when given a list
        and to print the pairs.  Also contains private method(s)
    '''

    def __init__(self, name_list, number_receivers):
        self.number_receivers = number_receivers
        self.name_list = name_list

    def _select_names(self, giver, receiver_list):
        '''Given one name (giver) and a list of receivers (all not
            yet paired), selects a receiver from the list and creates
            a GiverReceiverPair object.  Returns said object. 
        '''
        receivers = list(receiver_list)
        if DEBUG: print 'receivers list from _select names',repr(receivers)
        receiver_picks = []
        for i in range(self.number_receivers):
            receiver = random.choice(receivers)
            receivers.remove(receiver)
            receiver_picks.append(receiver)
        if DEBUG: 
            print 'giver[0] from _select_names', giver[0]
            print 'receiver list comparing to', repr(receiver_picks)
        if (giver[0] not in receiver_picks): #giver cannot be same as receiver
            if DEBUG: print 'giver[0] not in receiver_picks'
            giver_receiver_match = GiverReceiverPair(giver[0], receiver_picks, giver[1])
            return giver_receiver_match
        else:
            return self._select_names(giver, receiver_list)

    def pair_names(self):
        '''Main functionality - takes a list of names and returns
            a list of GiverReceiverPair objects. If only name left
            in receiver_list is == giver, this method sets the list
            to empty and calls itself again.
        '''
        if DEBUG: print 'pair names'
        giver_list = list(self.name_list)
        if DEBUG: print 'name_list', self.name_list
        receiver_dict = {}
        list_of_giver_receivers = []
        for receiver in self.name_list:
            receiver_dict[receiver[0]] = 0
        for name in giver_list:
            if ((len(receiver_dict) > self.number_receivers) or (len(receiver_dict) == self.number_receivers and name[0] not in receiver_dict)):
                print 'receiver_dict',repr(receiver_dict)
                print 'reciver_dict.keys()', receiver_dict.keys()
                giver_receiver = self._select_names(name, receiver_dict.keys())
                print 'receiver(s) from selector:', repr(giver_receiver.receiver)
                for receiver in giver_receiver.receiver:
                    print 'receiver: ',receiver
                    receiver_dict[receiver] += 1
                    if receiver_dict[receiver] >= self.number_receivers:
                        del receiver_dict[receiver]
                list_of_giver_receivers.append(giver_receiver)
            else:
                return self.pair_names()
        return list_of_giver_receivers#, self.person_list

    def print_pairs(self, giver_receiver_pairs):
        '''Method to print the generated giver/receiver pairs.
            Takes a GiverReceiverPair object as input.
            Returns nothing.
        '''
        if DEBUG: print 'print_pairs called:'
        for pair in giver_receiver_pairs:
            print pair.giver + " : " + repr(pair.receiver) + ', email: ' + pair.giver_email + '\n'
        return
