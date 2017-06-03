#!/usr/bin/python3

# global requirements
import json
import logging

# local requirements
from .Exceptions import *
from .JPARHandler import *
from .ConnectionHandler import *

# class KP
class LowLevelKP:

    """This is the Low-level class used to develop a KP"""

    # constructor
    def __init__(self, jparFile, jsapHandler = None, logLevel = 10):
        
        """Constructor for the Low-level KP class"""

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== KP::__init__ invoked ===")

        # load the jpar file
        self.jparHandler = JPARHandler(jparFile)

        # save the jsap handler
        self.jsapHandler = jsapHandler

        # initialize data structures
        self.subscriptions = {}

        # initialize handler
        self.connectionManager = ConnectionHandler(self.jparHandler, self.jsapHandler)


    # update
    def update(self, sparqlUpdate, secure):

        """This method is used to perform a SPARQL update"""
        
        # debug print
        self.logger.debug("=== KP::update invoked ===")

        # perform the update request
        status, results = self.connectionManager.request(sparqlUpdate, False, secure)                

        # return
        if int(status) == 200:
            return True, results
        else:
            return False, results


    # query
    def query(self, sparqlQuery, secure):

        """This method is used to perform a SPARQL query"""

        # debug print
        self.logger.debug("=== KP::query invoked ===")
        
        # perform the query request
        status, results = self.connectionManager.request(sparqlQuery, True, secure)
        
        # return 
        if int(status) == 200:
            jresults = json.loads(results)
            if "error" in jresults:
                return False, jresults["error"]["message"]
            else:
                return True, jresults
        else:
            return False, results
        

    # susbscribe
    def subscribe(self, sparql, alias, handler, secure):

        # debug print
        self.logger.debug("=== KP::subscribe invoked ===")
      
        # start the subscription and return the ID
        subid = self.connectionManager.openWebsocket(sparql, alias, handler, secure)
        return subid
        
    
    # unsubscribe
    def unsubscribe(self, subid, secure):

        # debug print
        self.logger.debug("=== KP::unsubscribe invoked ===")

        # close the subscription, given the id
        self.connectionManager.closeWebsocket(subid, secure)

