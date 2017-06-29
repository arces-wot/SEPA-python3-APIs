#!/usr/bin/python3

# global requirements
import pdb
import json
import logging

# local requirements
from .Exceptions import *


# class
class JPARHandler:

    # constructor
    def __init__(self, jparFile):

        """Constructor for the JPAR Handler class"""

        # logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== JPARHandler::__init__ invoked ===")

        # store the file name
        self.jparFile = jparFile

        # open the jpar file
        try:
            with open(jparFile) as jparFileStream:
                self.jparDict = json.load(jparFileStream)
        except Exception as e:
            self.logger.error("Parsing of the JPAR file failed")
            raise JPARParsingException from e

        # initialize user data
        self.client_id = None
        self.client_name = None
        self.client_secret = None
        self.jwt = None
        self.expiry = None

        # initialize network data
        self.queryURI = None
        self.updateURI = None
        self.queryURIsec = None
        self.updateURIsec = None
        self.subscribeURI = None
        self.subscribeURIsec = None
        self.registerURI = None
        self.getTokenURI = None

        # read data
        self.readClientId()
        self.readClientName()
        self.readClientSecret()
        self.readToken()
        self.readNetworkConfig()


    # read network configuration 
    def readNetworkConfig(self):
       
        """This method reads the network configuration defined in the JPAR file"""
    
        # debug
        self.logger.debug("=== JPARHandler::readNetworkConfig invoked ===")

        # read the mandatory fields
        try:
        
            # URI for update
            self.updateURI = "http://%s:%s%s" % (self.jparDict["parameters"]["host"],
                                                 self.jparDict["parameters"]["ports"]["http"],
                                                 self.jparDict["parameters"]["paths"]["update"])
            
            # URI for query        
            self.queryURI = "http://%s:%s%s" % (self.jparDict["parameters"]["host"],
                                                self.jparDict["parameters"]["ports"]["http"],
                                                self.jparDict["parameters"]["paths"]["query"])
            
            # URI for secure update
            self.updateURIsec = "https://%s:%s%s%s" % (self.jparDict["parameters"]["host"],
                                                     self.jparDict["parameters"]["ports"]["https"],
                                                     self.jparDict["parameters"]["paths"]["securePath"],
                                                     self.jparDict["parameters"]["paths"]["update"])
            
            # URI for secure query        
            self.queryURIsec = "https://%s:%s%s%s" % (self.jparDict["parameters"]["host"],
                                                    self.jparDict["parameters"]["ports"]["https"],
                                                    self.jparDict["parameters"]["paths"]["securePath"],
                                                    self.jparDict["parameters"]["paths"]["query"])
            
            # URI for subscriptions
            self.subscribeURI = "ws://%s:%s%s" % (self.jparDict["parameters"]["host"],
                                                  self.jparDict["parameters"]["ports"]["ws"],
                                                  self.jparDict["parameters"]["paths"]["subscribe"])
        
            # URI for secure subscriptions
            self.subscribeURIsec = "wss://%s:%s%s%s" % (self.jparDict["parameters"]["host"],
                                                        self.jparDict["parameters"]["ports"]["wss"],
                                                        self.jparDict["parameters"]["paths"]["securePath"],
                                                        self.jparDict["parameters"]["paths"]["subscribe"])

            # URI for registration
            self.registerURI = "https://%s:%s%s" % (self.jparDict["parameters"]["host"],
                                                   self.jparDict["parameters"]["ports"]["https"],
                                                   self.jparDict["parameters"]["paths"]["register"])
            
            # URI for token request
            self.getTokenURI = "https://%s:%s%s" % (self.jparDict["parameters"]["host"],
                                                    self.jparDict["parameters"]["ports"]["https"],
                                                    self.jparDict["parameters"]["paths"]["tokenRequest"])
            
        except KeyError as ex:
            self.logger.error("Not all the mandatory fields have been specified")
            raise JPARParsingException from ex
        
        
    # read client_id
    def readClientId(self):
        
        """Retrieves the client id form file, if present"""
        
        try:
            self.client_id = self.jparDict["client_id"]
        except KeyError:
            pass


    # read client_id
    def readClientName(self):
        
        """Retrieves the client id form file, if present"""
        
        try:
            self.client_name = self.jparDict["client_name"]
        except KeyError:
            pass


    # read client_secret
    def readClientSecret(self):
        
        """Retrieves the client secret form file, if present"""
        
        try:
            self.client_secret = self.jparDict["client_secret"]
        except KeyError:
            pass


    # read token
    def readToken(self):
        
        """Retrieves the token form file, if present"""
        
        try:
            self.jwt = self.jparDict["jwt"]
        except KeyError:
            pass


    # store config
    def storeConfig(self):

        """Method used to update the content of the JPAR file"""

        # store data into file
        jparFileStream = open(self.jparFile, "w")
        jparFileStream.write(json.dumps(self.jparDict))
