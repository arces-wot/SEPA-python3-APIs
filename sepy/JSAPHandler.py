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
        self.logger.debug("=== JSAPHandler::__init__ invoked ===")

        # open sapFile
        try:
            with open(sapFile) as sapFileStream:
                self.jsapDict = json.load(sapFileStream)
        except Exception as e:
            self.logger.error("Parsing of the JSAP file failed")
            raise JSAPParsingException from e

        # initialize URIs
        self.queryURI = None
        self.updateURI = None
        self.queryURIsec = None
        self.updateURIsec = None
        self.subscribeURI = None
        self.subscribeURIsec = None
        self.registerURI = None
        self.getTokenURI = None

        # initialize structures
        self.namespaces = {}
        self.queries = {}
        self.updates = {}
        self.nconfig = {}

        # fill every structure
        self.readNamespaces()
        self.readQueries()
        self.readUpdates()
        self.readNetworkConfig()        
            

    # read network configuration 
    def readNetworkConfig(self):
       
        """This method reads the network configuration defined in the JSAP file"""
    
        # debug
        self.logger.debug("=== JSAPHandler::readNetworkConfig invoked ===")

        # read the mandatory fields
        try:
        
            # URI for update
            self.updateURI = "http://%s:%s%s" % (self.jsapDict["parameters"]["host"],
                                                 self.jsapDict["parameters"]["ports"]["http"],
                                                 self.jsapDict["parameters"]["paths"]["update"])
            
            # URI for query        
            self.queryURI = "http://%s:%s%s" % (self.jsapDict["parameters"]["host"],
                                                self.jsapDict["parameters"]["ports"]["http"],
                                                self.jsapDict["parameters"]["paths"]["query"])
            
            # URI for secure update
            self.updateURIsec = "https://%s:%s%s%s" % (self.jsapDict["parameters"]["host"],
                                                     self.jsapDict["parameters"]["ports"]["https"],
                                                     self.jsapDict["parameters"]["paths"]["securePath"],
                                                     self.jsapDict["parameters"]["paths"]["update"])
            
            # URI for secure query        
            self.queryURIsec = "https://%s:%s%s%s" % (self.jsapDict["parameters"]["host"],
                                                    self.jsapDict["parameters"]["ports"]["https"],
                                                    self.jsapDict["parameters"]["paths"]["securePath"],
                                                    self.jsapDict["parameters"]["paths"]["query"])
            
            # URI for subscriptions
            self.subscribeURI = "ws://%s:%s%s" % (self.jsapDict["parameters"]["host"],
                                                  self.jsapDict["parameters"]["ports"]["ws"],
                                                  self.jsapDict["parameters"]["paths"]["subscribe"])
        
            # URI for secure subscriptions
            self.subscribeURIsec = "wss://%s:%s%s%s" % (self.jsapDict["parameters"]["host"],
                                                        self.jsapDict["parameters"]["ports"]["wss"],
                                                        self.jsapDict["parameters"]["paths"]["securePath"],
                                                        self.jsapDict["parameters"]["paths"]["subscribe"])

            # URI for registration
            self.registerURI = "https://%s:%s%s" % (self.jsapDict["parameters"]["host"],
                                                   self.jsapDict["parameters"]["ports"]["https"],
                                                   self.jsapDict["parameters"]["paths"]["register"])
            
            # URI for token request
            self.getTokenURI = "https://%s:%s%s" % (self.jsapDict["parameters"]["host"],
                                                    self.jsapDict["parameters"]["ports"]["https"],
                                                    self.jsapDict["parameters"]["paths"]["tokenRequest"])
            
        except KeyError as ex:
            self.logger.error("Not all the mandatory fields have been specified")
            raise JSAPParsingException from ex


    # read namespaces
    def readNamespaces(self):
        
        """This method is used to read namespaces"""

        # debug
        self.logger.debug("=== JSAPHandler::readNamespaces invoked ===")
        
        # iterate over the namespaces keys
        try:
            for nsname in self.jsapDict["namespaces"].keys():
                self.namespaces[nsname] = self.jsapDict["namespaces"][nsname]
        except KeyError:
            pass


    # read queries/subscriptions
    def readQueries(self):

        """This method reads the queries defined in the JSAP file"""

        # debug
        self.logger.debug("=== JSAPHandler::readQueries invoked ===")

        # iterate over queries
        try:
            for qname in self.jsapDict["queries"]:
                self.queries[qname] = self.jsapDict["queries"][qname]
        except KeyError:
            pass

        
    # read updates
    def readUpdates(self):
        
        """This method reads the updates defined in the JSAP file"""

        # debug
        self.logger.debug("=== JSAPHandler::readUpdates invoked ===")

        # iterate over updates
        try:
            for uname in self.jsapDict["updates"]:
                self.updates[uname] = self.jsapDict["updates"][uname]
        except KeyError:
            pass


    # utility to build URIs
    def buildURI(self, manField, dictKey):

        """Utility to build URIs based on the configuration"""

        # debug
        self.logger.debug("=== JSAPHandler::buildURI invoked ===")
        
        # initialize overwriting variables
        oprot = ohost = oport = opath = None

        # read overwriting config for the connection protocol
        try:
            oprot = self.jsapDict["parameters"][dictKey]["scheme"]
        except KeyError:
            pass

        # read overwriting config for the connection host
        try:
            ohost = self.jsapDict["parameters"][dictKey]["host"]
        except KeyError:
            pass

        # read overwriting config for the connection port
        try:
            oport = self.jsapDict["parameters"][dictKey]["port"]
        except KeyError:
            pass

        # read overwriting config for the path
        try:
            opath = self.jsapDict["parameters"][dictKey]["path"]
        except KeyError:
            pass

        # build and return the final URI
        return "%s://%s:%s%s" % ((oprot if (oprot) else manField["prot"]),
                                 (ohost if (ohost) else manField["host"]),
                                 (oport if (oport) else manField["port"]),
                                 (opath if (opath) else manField["path"]))


    def buildRegistrationURIs(self, manField):

        """Utility to build registration URIs based on the configuration"""

        # debug
        self.logger.debug("=== JSAPHandler::buildRegistrationURI invoked ===")
        
        # initialize overwriting variables
        oprot = ohost = oport = None    

        # read overwriting config for the connection protocol
        try:
            oprot = self.jsapDict["parameters"]["authorizationServer"]["scheme"]
        except KeyError:
            pass

        # read overwriting config for the connection host
        try:
            ohost = self.jsapDict["parameters"]["authorizationServer"]["host"]
        except KeyError:
            pass

        # read overwriting config for the connection port
        try:
            oport = self.jsapDict["parameters"]["authorizationServer"]["port"]
        except KeyError:
            pass

        # build and return the final URI
        return ["%s://%s:%s%s" % ((oprot if (oprot) else manField["prot"]),
                                  (ohost if (ohost) else manField["host"]),
                                  (oport if (oport) else manField["port"]),
                                  self.jsapDict["parameters"]["authorizationServer"]["register"]),
                "%s://%s:%s%s" % ((oprot if (oprot) else manField["prot"]),
                                  (ohost if (ohost) else manField["host"]),
                                  (oport if (oport) else manField["port"]),
                                  self.jsapDict["parameters"]["authorizationServer"]["requestToken"])]


    # get query
    def getQuery(self, queryName, userForcedBindings):

        """Utility to retrieve a query"""

        # debug
        self.logger.debug("=== JSAPHandler::getQuery invoked ===")

        # initialize the final string
        q = self.getNamespaces()
      
        # get the template of the SPARQL update
        tquery = self.queries[queryName]["sparql"]

        # iterate over the forcedBindings given by the user
        # for every forcedBidings we check if it's present 
        # in the update definition taken from the JSAP
        for qfb in userForcedBindings.keys():
            if qfb in self.queries[queryName]["forcedBindings"]:
                
                # replace the fake variable with the provided value
                # according to the type defined in the JSAP file
                if self.queries[queryName]["forcedBindings"][qfb]["type"].lower() == "uri":
                    tquery = tquery.replace("?%s" % qfb, " <%s> " % userForcedBindings[qfb])
                elif self.queries[queryName]["forcedBindings"][qfb]["type"].lower() == "literal":
                    tquery = tquery.replace("?%s" % qfb, ' \"%s\" ' % userForcedBindings[qfb])
        
        # build the final update
        return self.getNamespaces() + tquery


    # get update
    def getUpdate(self, updateName, userForcedBindings):

        """Utility to retrieve an update"""

        # debug
        self.logger.debug("=== JSAPHandler::getUpdate invoked ===")

        # initialize the final string
        u = self.getNamespaces()
      
        # get the template of the SPARQL update
        tupdate = self.updates[updateName]["sparql"]

        # iterate over the forcedBindings given by the user
        # for every forcedBidings we check if it's present 
        # in the update definition taken from the JSAP
        for ufb in userForcedBindings.keys():
            if ufb in self.updates[updateName]["forcedBindings"]:
                
                # replace the fake variable with the provided value
                # according to the type defined in the JSAP file
                if self.updates[updateName]["forcedBindings"][ufb]["type"].lower() == "uri":
                    self.logger.debug("Replacing " + ufb + " with " + userForcedBindings[ufb])
                    tupdate = tupdate.replace("?%s " % ufb, " %s " % userForcedBindings[ufb])
                elif self.updates[updateName]["forcedBindings"][ufb]["type"].lower() == "literal":
                    tupdate = tupdate.replace("?%s " % ufb, ' "%s" ' % userForcedBindings[ufb])
        
        # build the final update
        return self.getNamespaces() + tupdate


    # get namespaces
    def getNamespaces(self):

        """Utility to build the namespace section of a SPARQL query/update"""

        # debug
        self.logger.debug("=== JSAPHandler::getNamespaces invoked ===")

        # initialize the final string
        prefixes = ""
        
        # define a template for a prefix line
        tprefix = "PREFIX %s: <%s> "
        
        # iterate over namespaces
        for ns in self.namespaces.keys():        
            prefixes += tprefix % (ns, self.namespaces[ns])

        # return
        return prefixes

