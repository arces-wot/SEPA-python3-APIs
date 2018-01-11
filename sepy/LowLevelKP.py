#!/usr/bin/python3

# global requirements
import json
import logging

# local requirements
from .Exceptions import *
from .ConnectionHandler import *

# class KP
class LowLevelKP:

    """This is the Low-level class used to develop a KP"""

    # constructor
    def __init__(self, jparFile = None, logLevel = 10):
        
        """Constructor for the Low-level KP class"""

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== KP::__init__ invoked ===")

        # initialize data structures
        self.subscriptions = {}

        # initialize handler
        self.connectionManager = ConnectionHandler(jparFile)


    # update
    def update(self, updateURI, sparqlUpdate, secure = False, tokenURI = None, registerURI = None):

        """This method is used to perform a SPARQL update"""
        
        # debug print
        self.logger.debug("=== KP::update invoked ===")

        # perform the update request
        if secure:
            status, results = self.connectionManager.secureRequest(updateURI, sparqlUpdate, False, tokenURI, registerURI)
        else:
            status, results = self.connectionManager.unsecureRequest(updateURI, sparqlUpdate, False)

        # return
        if int(status) == 200:
            return True, results
        else:
            return False, results


    # query
    def query(self, queryURI, sparqlQuery, secure = False, tokenURI = None, registerURI = None):

        """This method is used to perform a SPARQL query"""

        # debug print
        self.logger.debug("=== KP::query invoked ===")
        
        # perform the query request
        if secure:
            status, results = self.connectionManager.secureRequest(queryURI, sparqlQuery, True, tokenURI, registerURI)
        else:
            status, results = self.connectionManager.unsecureRequest(queryURI, sparqlQuery, True)
            
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
    def subscribe(self, subscribeURI, sparql, alias, handler, secure = False, registerURI = None, tokenURI = None):

        # debug print
        self.logger.debug("=== KP::subscribe invoked ===")
      
        # start the subscription and return the ID
        subid = None
        if secure:
            print("HERE")
            subid = self.connectionManager.openSecureWebsocket(subscribeURI, sparql, alias, handler, registerURI, tokenURI)
        else:
            subid = self.connectionManager.openUnsecureWebsocket(subscribeURI, sparql, alias, handler)
        return subid
        
    
    # unsubscribe
    def unsubscribe(self, subid, secure):

        # debug print
        self.logger.debug("=== KP::unsubscribe invoked ===")

        # close the subscription, given the id
        self.connectionManager.closeWebsocket(subid, secure)

