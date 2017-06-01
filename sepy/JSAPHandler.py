#!/usr/bin/python3

# global requirements
import json
import logging

# local requirements
from .Exceptions import *


# class
class JSAPHandler:

    # constructor
    def __init__(self, sapFile):

        """Constructor for the JSAP Handler class"""

        # logger
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== JSAPHandler::__init__ invoked ===")

        # open sapFile
        try:
            self.sapDict = json.loads(sapFile)
        except JSONDecodeError:
            logger.error("Parsing of the JSAP file failed")
            raise SapParsingException

        # initialize URIs
        self.queryURI = None
        self.updateURI = None
        self.queryURIsec = None
        self.updateURIsec = None
        self.subscribeURI = None
        self.subscribeURIsec = None

        # initialize structures
        self.queries = {}
        self.updates = {}
        self.nconfig = {}
            

    # read network configuration 
    def readNetworkConfig(self):
       
         """This method reads the network configuration defined in the JSAP file"""

        # debug
        logger.debug("=== JSAPHandler::readNetworkConfig invoked ===")

        # read the mandatory fields
        manField = {}
        try:
            manField["prot"] = self.sapDict["parameters"]["scheme"],
            manField["host"] = self.sapDict["parameters"]["host"],
            manField["port"] = self.sapDict["parameters"]["port"],
            manField["path"] = self.sapDict["parameters"]["path"]
        except KeyError:
            logger.error("Not all the mandatory fields have been specified")
            raise SapParsingException

        # build URIs
        self.queryURI = self.buildURI(manField, "query")
        self.updateURI = self.buildURI(manField, "update")
        self.queryURIsec = self.buildURI(manField, "secureQuery")
        self.updateURIsec = self.buildURI(manField, "secureUpdate")
        self.subscribeURI = self.buildURI(manField, "subscribe")
        self.subscribeURIsec = self.buildURI(manField, "secureSubscribe")


    # read queries/subscriptions
    def readQueries(self):

        """This method reads the queries defined in the JSAP file"""

        # debug
        logger.debug("=== JSAPHandler::readQueries invoked ===")

        
    # read updates
    def readUpdates(self):
        
        """This method reads the updates defined in the JSAP file"""

        # debug
        logger.debug("=== JSAPHandler::readUpdates invoked ===")


    # utility to build URIs
    def buildURI(manField, dictKey):

        """Utility to build URIs based on the configuration"""

        # debug
        logger.debug("=== JSAPHandler::buildURI invoked ===")
        
        # initialize overwriting variables
        oprot = ohost = oport = opath = None

        # read overwriting config for the connection protocol
        try:
            oprot = self.sapDict["parameters"][dictKey]["scheme"],
        except KeyError:
            pass

        # read overwriting config for the connection host
        try:
            ohost = self.sapDict["parameters"][dictKey]["host"],
        except KeyError:
            pass

        # read overwriting config for the connection port
        try:
            oport = self.sapDict["parameters"][dictKey]["port"],
        except KeyError:
            pass

        # read overwriting config for the path
        try:
            opath = self.sapDict["parameters"][dictKey]["path"]
        except KeyError:
            pass

        # build and return the final URI
        return "%s://%s:%s%s" % ((oprot if (oprot) else manField["prot"]),
                                 (ohost if (ohost) else manField["host"]),
                                 (oport if (oport) else manField["port"]),
                                 (opath if (opath) else manField["path"]))
