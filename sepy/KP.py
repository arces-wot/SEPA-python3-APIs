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
    def __init__(self, host, path, registrationPath, tokenReqPath, # paths
                 httpPort, httpsPort, wsPort, wssPort, # ports                 
                 secure, clientName, logLevel): # security and debug
        
        """Constructor for the Low-level KP class"""

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== KP::__init__ invoked ===")

        # initialize data structures
        self.subscriptions = {}

        # initialize handler
        self.connectionManager = ConnectionHandler(host, path, registrationPath, tokenReqPath, # paths
                                                   httpPort, httpsPort, wsPort, wssPort, # ports
                                                   secure, clientName) # security


    # update
    def update(self, sparqlUpdate):

        """This method is used to perform a SPARQL update"""
        
        # debug print
        self.logger.debug("=== KP::update invoked ===")

        # perform the update request
        status, results = self.connectionManager.request(sparqlUpdate, False)                

        # return
        if int(status) == 200:
            return True, results
        else:
            return False, results


    # query
    def query(self, sparqlQuery):

        """This method is used to perform a SPARQL query"""

        # debug print
        self.logger.debug("=== KP::query invoked ===")
        
        # perform the query request
        status, results = self.connectionManager.request(sparqlQuery, True)

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
    def subscribe(self, sparql, alias, handler):

        # debug print
        self.logger.debug("=== KP::subscribe invoked ===")
      
        # start the subscription and return the ID
        subid = self.connectionManager.openWebsocket(sparql, alias, handler)
        return subid
        
    
    # unsubscribe
    def unsubscribe(self, subid):

        # debug print
        self.logger.debug("=== KP::unsubscribe invoked ===")

        # close the subscription, given the id
        self.connectionManager.closeWebsocket(subid)

