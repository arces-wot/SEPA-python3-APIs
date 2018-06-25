#!/usr/bin/python3

import json
import logging
from .Exceptions import *
from .ConnectionHandler import *

# class KP
class SEPAClient:

    """
    This is the Low-level class used to develop a client for SEPA.

    Parameters
    ----------
    jparFile : str
        Name with relative/full path of the JPAR file used to exploit the security mechanism (default = None)
    logLevel : int
        The desired log level. Default = 40

    Attributes
    ----------
    subscriptions : dict
        Dictionary to keep track of the active subscriptions
    connectionManager : ConnectionManager
        The underlying responsible for network connections

    """

    # constructor
    def __init__(self, jparFile = None, logLevel = 40, lastSEPA = False):
        
        """
        Constructor for the Low-level KP class

        Parameters
        ----------
        jparFile : str
            Name with relative/full path of the JPAR file used to exploit the security mechanism (default = None)
        logLevel : int
            The desired log level. Default = 40

        """

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        self.logger.setLevel(logLevel)
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== KP::__init__ invoked ===")

        # initialize data structures
        self.subscriptions = {}

        # initialize handler
        self.connectionManager = ConnectionHandler(jparFile, logLevel, lastSEPA)


    # update
    def update(self, updateURI, sparqlUpdate, secure = False, tokenURI = None, registerURI = None):

        """
        This method is used to perform a SPARQL update

        Parameters
        ----------
        updateURI : str
            The URI of the SEPA instances used for update requests
        sparqlUpdate : str
            The SPARQL update to perform
        secure : bool
            A boolean that states if the connection must be secure or not (default = False)
        tokenURI : str
            The URI to request token if using a secure connection (default = None)
        registerURI : str
            The URI to register if using a secure connection (default = None)

        Returns
        -------
        status : bool
            True or False, depending on the success/failure of the request
        results : json
            The results of the SPARQL update

        """
        
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
    
        """
        This method is used to perform a SPARQL query

        Parameters
        ----------
        queryURI : str
            The URI of the SEPA instances used for query requests
        sparqlQuery : str
            The SPARQL query to perform
        secure : bool
            A boolean that states if the connection must be secure or not (default = False)
        tokenURI : str
            The URI to request token if using a secure connection (default = None)
        registerURI : str
            The URI to register if using a secure connection (default = None)

        Returns
        -------
        status : bool
            True or False, depending on the success/failure of the request
        results : json
            The results of the SPARQL query

        """

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

        """
        This method is used to start a SPARQL subscription

        Parameters
        ----------
        subscribeURI : str
            The URI of the SEPA instances used for update requests
        sparql : str
            The SPARQL subscription to request
        alias : str
            A friendly name for the subscription
        handler : Handler
            A class to handle notifications
        secure : bool
            A boolean that states if the connection must be secure or not (default = False)
        tokenURI : str
            The URI to request token if using a secure connection (default = None)
        registerURI : str
            The URI to register if using a secure connection (default = None)

        Returns
        -------
        subid : str
            The id of the subscription, useful to call the unsubscribe method

        """
        
        # debug print
        self.logger.debug("=== KP::subscribe invoked ===")
      
        # start the subscription and return the ID
        subid = None
        if secure:
            subid = self.connectionManager.openSecureWebsocket(subscribeURI, sparql, alias, handler, registerURI, tokenURI)
        else:
            subid = self.connectionManager.openUnsecureWebsocket(subscribeURI, sparql, alias, handler)
        return subid
        
    
    # unsubscribe
    def unsubscribe(self, subid, secure):

        """
        This method is used to start a SPARQL subscription

        Parameters
        ----------
        subid : str
            The id of the subscription
        secure : bool
            A boolean that states if the connection must be secure or not (default = False)

        """
        
        # debug print
        self.logger.debug("=== KP::unsubscribe invoked ===")

        # close the subscription, given the id
        self.connectionManager.closeWebsocket(subid, secure)

