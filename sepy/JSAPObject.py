#!/usr/bin/python3

# global requirements
import logging
import json
import re

# the class
class JSAPObject:

    """A class to handle JSAP files"""

    def __init__(self, jsapFile):

        """Constructor of the JSAPObject class"""

        # logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== JSAPObject::__init__ invoked ===")

        # try to open JSAP File
        try:
            with open(jsapFile) as jsapFileStream:
                self.jsapDict = json.load(jsapFileStream)
        except Exception as e:
            self.logger.error("Parsing of the JSAP file failed")
            raise JSAPParsingException from e        

        # try to read the network configuration
        try:
            host = self.jsapDict["parameters"]["host"]
            httpPort = self.jsapDict["parameters"]["ports"]["http"]
            httpsPort = self.jsapDict["parameters"]["ports"]["https"]
            wsPort = self.jsapDict["parameters"]["ports"]["ws"]
            wssPort = self.jsapDict["parameters"]["ports"]["wss"]
            queryPath = self.jsapDict["parameters"]["paths"]["query"]
            updatePath = self.jsapDict["parameters"]["paths"]["update"]
            subscribePath = self.jsapDict["parameters"]["paths"]["subscribe"]
            registerPath = self.jsapDict["parameters"]["paths"]["register"]
            tokenRequestPath = self.jsapDict["parameters"]["paths"]["tokenRequest"]
            securePath = self.jsapDict["parameters"]["paths"]["securePath"]
        except KeyError as e:
            self.logger.error("Network configuration incomplete in JSAP file")
            raise JSAPParsingExcepction from e

        # define attributes for secure connection
        self.secureSubscribeUri = "wss://%s:%s%s%s" % (host, wssPort, securePath, subscribePath)
        self.secureUpdateUri = "https://%s:%s%s%s" % (host, httpsPort, securePath, updatePath)
        self.secureQueryUri = "https://%s:%s%s%s" % (host, httpsPort, securePath, queryPath)
        
        # define attributes for unsecure connection
        self.subscribeUri = "ws://%s:%s%s" % (host, wsPort, subscribePath)
        self.updateUri = "http://%s:%s%s" % (host, httpPort, updatePath)
        self.queryUri = "http://%s:%s%s" % (host, httpPort, queryPath)

        # define attributes for registration and token request
        self.tokenReqUri = "https://%s:%s%s" % (host, httpsPort, tokenRequestPath)
        self.registerUri = "https://%s:%s%s" % (host, httpsPort, registerPath)

        # read namespaces
        self.namespaces = {}
        try:
            self.namespaces = self.jsapDict["namespaces"]
        except KeyError:            
            pass

        # define namespace sparql string
        self.nsSparql = ""
        for ns in self.namespaces.keys():
            self.nsSparql += "PREFIX %s: <%s> " % (ns, self.namespaces[ns])

        # read queries
        self.queries = {}
        try:
            self.queries = self.jsapDict["queries"]
        except KeyError:            
            pass

        # read updates
        self.updates = {}
        try:
            self.namespaces = self.jsapDict["updates"]
        except KeyError:            
            pass


    def getQuery(self, queryName, forcedBindings):

        """Method used to get the final query text"""

        # debug print
        self.logger.debug("=== JSAPObject::getQuery invoked ===")

        # call getSparql
        return self.getSparql(True, queryName, forcedBindings)


    def getUpdate(self, updateName, forcedBindings):

        """Method used to get the final update text"""

        # debug print
        self.logger.debug("=== JSAPObject::getUpdate invoked ===")

        # call getSparql
        return self.getSparql(False, updateName, forcedBindings)


    def getSparql(self, isQuery, sparqlName, forcedBindings):

        """Retrieves a sparql query or update and substitutes
        the forced bindings to get the final sparql code"""

        # debug print
        self.logger.debug("=== JSAPObject::getSparql invoked ===")

        # initialize
        jsapSparql = None
        jsapForcedBindings = None

        # determine if it is query or update
        if isQuery:

            # read the initial query
            try:
                jsapSparql = self.queries[sparqlName]["sparql"]
                jsapForcedBindings = self.queries[sparqlName]["forcedBindings"]
            except KeyError:
                self.logger.error("Query not found in JSAP file")
                raise JSAPParsingExcepction from e
        
        else:

            # read the initial update
            try:
                jsapSparql = self.updates[sparqlName]["sparql"]
                jsapForcedBidnings = self.updates[sparqlName]["forcedBindings"]
            except KeyError:
                self.logger.error("Update not found in JSAP file")
                raise JSAPParsingExcepction from e
        
        # for every forced binding perform a substitution
        for v in forcedBindings.keys():

            # check if v is in the jsap forced bindings
            if v in jsapForcedBindings.keys():
            
                # determine the variable replacement
                value = forcedBindings[v]

                # debug print
                self.logger.debug("Replacing variable " + v + " with " + value) 

                # replace the variable when it is followed by a space
                jsapSparql = re.sub(r'(\?|\$){1}' + v + r'\s+', value + " ", jsapSparql, flags=0)

                # replace the variable when it is followed by a dot
                jsapSparql = re.sub(r'(\?|\$){1}' + v + r'\.', value + " . ", jsapSparql, flags=0)

        # return
        return self.nsSparql + jsapSparql
