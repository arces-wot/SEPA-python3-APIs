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
        manField = {}
        try:
            manField["prot"] = self.jparDict["parameters"]["scheme"]
            manField["host"] = self.jparDict["parameters"]["host"]
            manField["port"] = self.jparDict["parameters"]["port"]
            manField["path"] = self.jparDict["parameters"]["path"]
        except KeyError as ex:
            self.logger.error("Not all the mandatory fields have been specified")
            raise SapParsingException from ex

        # build URIs
        self.queryURI = self.buildURI(manField, "query")
        print(self.queryURI)
        self.updateURI = self.buildURI(manField, "update")
        self.queryURIsec = self.buildURI(manField, "secureQuery")
        self.updateURIsec = self.buildURI(manField, "secureUpdate")
        self.subscribeURI = self.buildURI(manField, "subscribe")
        self.subscribeURIsec = self.buildURI(manField, "secureSubscribe")

        # build registration URIs
        self.registerURI, self.getTokenURI = self.buildRegistrationURIs(manField)
        
        
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


    # utility to build URIs
    def buildURI(self, manField, dictKey):

        """Utility to build URIs based on the configuration"""

        # debug
        self.logger.debug("=== JPARHandler::buildURI invoked ===")
        
        # initialize overwriting variables
        oprot = ohost = oport = opath = None

        # read overwriting config for the connection protocol
        try:
            oprot = self.jparDict["parameters"][dictKey]["scheme"]
        except KeyError:
            pass

        # read overwriting config for the connection host
        try:
            ohost = self.jparDict["parameters"][dictKey]["host"]
        except KeyError:
            pass

        # read overwriting config for the connection port
        try:
            oport = self.jparDict["parameters"][dictKey]["port"]
        except KeyError:
            pass

        # read overwriting config for the path
        try:
            opath = self.jparDict["parameters"][dictKey]["path"]
        except KeyError:
            pass

        # build and return the final URI
        return "%s://%s:%s%s" % (oprot if oprot else manField["prot"],
                                 ohost if ohost else manField["host"],
                                 oport if oport else manField["port"],
                                 opath if opath else manField["path"])


    # registration URIs
    def buildRegistrationURIs(self, manField):

        """Utility to build registration URIs based on the configuration"""

        # debug
        self.logger.debug("=== JPARHandler::buildRegistrationURI invoked ===")
        
        # initialize overwriting variables
        oprot = ohost = oport = None    

        # read overwriting config for the connection protocol
        try:
            oprot = self.jparDict["parameters"]["authorizationServer"]["scheme"]
        except KeyError:
            pass

        # read overwriting config for the connection host
        try:
            ohost = self.jparDict["parameters"]["authorizationServer"]["host"]
        except KeyError:
            pass

        # read overwriting config for the connection port
        try:
            oport = self.jparDict["parameters"]["authorizationServer"]["port"]
        except KeyError:
            pass

        # build and return the final URI
        return ["%s://%s:%s%s" % (oprot if (oprot) else manField["prot"],
                                  ohost if (ohost) else manField["host"],
                                  oport if (oport) else manField["port"],
                                  self.jparDict["parameters"]["authorizationServer"]["register"]),
                "%s://%s:%s%s" % (oprot if (oprot) else manField["prot"],
                                  ohost if (ohost) else manField["host"],
                                  oport if (oport) else manField["port"],
                                  self.jparDict["parameters"]["authorizationServer"]["requestToken"])]


    # store config
    def storeConfig(self):

        """Method used to update the content of the JPAR file"""

        # store data into file
        jparFileStream = open(self.jparFile, "w")
        jparFileStream.write(json.dumps(self.jparDict))
