#!/usr/bin/python3

from .Exceptions import *
import logging
import json
import re


class JSAPObject:

    """
    A class to handle JSAP files

    Parameters
    ----------
    jsapFile : str
        The name (with relative or absolute path) of the JSAP file
    logLevel : int
        The desired level of debugging information (default = 40)
    
    Attributes
    ----------
    jsap : dict
        The full dictionary with the JSAP content
    namespaces : dict
        Dictionary with prefixes (keys) and namespaces (values)
    queries : dict
        Dictionary with SPARQL query templates (values) indexed by a friendly name (key)
    updates : dict
        Dictionary with SPARQL update templates (values) indexed by a friendly name (key)
    updateURI : str
        The URI to perform SPARQL updates
    queryURI : str
        The URI to perform SPARQL queries
    subscribeURI : str
        The URI to perform SPARQL subscriptions
    host : str
        The hostname of the SEPA instance
    httpPort : int
        The port number for unsecure HTTP connection
    httpsPort : int
        The port number for secure HTTP connection
    wsPort : int
        The port number for unsecure Websocket connection
    wssPort : int
        The port number for secure Websocket connection
    queryPath : str
        The path to the query resource of the SEPA instance
    updatePath : str
        The path to the update resource of the SEPA instance
    subscribePath : str
        The path to the subscribe resource of the SEPA instance
    registerPath : str
        The path to register to the SEPA instance
    tokenRequestPath : str
        The path to request a token for secure connections to the SEPA instance
    securePath : str
        The path to compose URIs for secure connections to SEPA
    """

    def __init__(self, jsapFile, logLevel = 10):

        """
        Constructor of the JSAPObject class

        Parameters
        ----------
        jsapFile : str
            The name (with relative or absolute path) of the JSAP file
        logLevel : int
            The desired level of debugging information (default = 40)
    
        """

        # logger
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.setLevel(logLevel)
        self.logger.debug("=== JSAPObject::__init__ invoked ===")

        # try to open JSAP File
        try:
            with open(jsapFile) as jsapFileStream:
                self.jsapDict = json.load(jsapFileStream)
        except Exception as e:
            self.logger.error("Parsing of the JSAP file failed")
            raise JSAPParsingException("Parsing of the JSAP file failed")        

        # try to read the network configuration
        try:
            self.host = self.jsapDict["parameters"]["host"]
            self.httpPort = self.jsapDict["parameters"]["ports"]["http"]
            self.httpsPort = self.jsapDict["parameters"]["ports"]["https"]
            self.wsPort = self.jsapDict["parameters"]["ports"]["ws"]
            self.wssPort = self.jsapDict["parameters"]["ports"]["wss"]
            self.queryPath = self.jsapDict["parameters"]["paths"]["query"]
            self.updatePath = self.jsapDict["parameters"]["paths"]["update"]
            self.subscribePath = self.jsapDict["parameters"]["paths"]["subscribe"]
            self.registerPath = self.jsapDict["parameters"]["paths"]["register"]
            self.tokenRequestPath = self.jsapDict["parameters"]["paths"]["tokenRequest"]
            self.securePath = self.jsapDict["parameters"]["paths"]["securePath"]
        except KeyError as e:
            self.logger.error("Network configuration incomplete in JSAP file")
            raise JSAPParsingException("Network configuration incomplete in JSAP file")

        # define attributes for secure connection
        self.secureSubscribeUri = "wss://%s:%s%s%s" % (self.host, self.wssPort, self.securePath, self.subscribePath)
        self.secureUpdateUri = "https://%s:%s%s%s" % (self.host, self.httpsPort, self.securePath, self.updatePath)
        self.secureQueryUri = "https://%s:%s%s%s" % (self.host, self.httpsPort, self.securePath, self.queryPath)
        
        # define attributes for unsecure connection
        self.subscribeUri = "ws://%s:%s%s" % (self.host, self.wsPort, self.subscribePath)
        self.updateUri = "http://%s:%s%s" % (self.host, self.httpPort, self.updatePath)
        self.queryUri = "http://%s:%s%s" % (self.host, self.httpPort, self.queryPath)

        # define attributes for registration and token request
        self.tokenReqUri = "https://%s:%s%s" % (self.host, self.httpsPort, self.tokenRequestPath)
        self.registerUri = "https://%s:%s%s" % (self.host, self.httpsPort, self.registerPath)

        # read namespaces
        self.namespaces = {}
        try:
            self.namespaces = self.jsapDict["namespaces"]
        except Exception as e:            
            raise JSAPParsingException("Error while reading namespaces of the JSAP file")

        # define namespace sparql string
        self.nsSparql = ""
        for ns in self.namespaces.keys():
            self.nsSparql += "PREFIX %s: <%s> " % (ns, self.namespaces[ns])

        # read queries
        self.queries = {}
        try:
            self.queries = self.jsapDict["queries"]
        except Exception as e:            
            raise JSAPParsingException("Error while reading queries of the JSAP file")

        # read updates
        self.updates = {}
        try:
            self.updates = self.jsapDict["updates"]
        except Exception as e:            
            raise JSAPParsingException("Error while reading updates of the JSAP file")


    def getQuery(self, queryName, forcedBindings):

        """
        Returns a SPARQL query retrieved from the YSAP and
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        queryName : str
            The friendly name of the SPARQL Query
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template

        Returns
        -------
        str
            The complete SPARQL Query
       
        """

        # debug print
        self.logger.debug("=== JSAPObject::getQuery invoked ===")

        # call getSparql
        return self.getSparql(True, queryName, forcedBindings)


    def getUpdate(self, updateName, forcedBindings):

        """
        Returns a SPARQL update retrieved from the YSAP and
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        updateName : str
            The friendly name of the SPARQL Update
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template

        Returns
        -------
        str
            The complete SPARQL Update
       
        """

        # debug print
        self.logger.debug("=== JSAPObject::getUpdate invoked ===")

        # call getSparql
        return self.getSparql(False, updateName, forcedBindings)


    def getSparql(self, isQuery, sparqlName, forcedBindings):
        
        """
        Returns a SPARQL query/update retrieved from the YSAP and 
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        isQuery : bool
            A variable to specify if looking for a query or an update
        sparqlName : str
            The friendly name of the SPARQL Update
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template

        Returns
        -------
        str
            The complete SPARQL Query or Update
        
        """

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
            except KeyError as e:
                self.logger.error("Query not found in JSAP file")
                raise JSAPParsingException("Query not found in JSAP file")
            
            try:
                jsapForcedBindings = self.queries[sparqlName]["forcedBindings"]
            except KeyError as e:
                self.logger.debug("No forcedBindings for the query {}".format(sparqlName))
        
        else:

            # read the initial update
            try:
                jsapSparql = self.updates[sparqlName]["sparql"]
                jsapForcedBindings = self.updates[sparqlName]["forcedBindings"]
            except KeyError as e:
                self.logger.error("Update not found in JSAP file")
                raise JSAPParsingException("Update not found in JSAP file")
        
        # for every forced binding perform a substitution
        for v in forcedBindings.keys():
            
            # check if v is in the jsap forced bindings
            if v in jsapForcedBindings.keys():
            
                # determine the variable replacement
                value = forcedBindings[v]
                valueType = jsapForcedBindings[v]["type"]

                if valueType=="literal":
                    value = "'{}'".format(value)
                else: 
                    # full uris between <>
                    namespace_node = False
                    for ns in self.namespaces:
                        r = re.compile("{}:.+".format(ns))
                        if r.match(value) is not None:
                            namespace_node = True
                            break
                    if not namespace_node:
                        value = "<{}>".format(value)
                        
                # debug print
                self.logger.debug("Replacing {} variable {} with {}".format(valueType,v,value)) 

                # replace the variable when it is followed by a space
                jsapSparql = re.sub(r'(\?|\$){1}' + v + r'\s+', value + " ", jsapSparql, flags=0)

                # replace the variable when it is followed by a braket
                jsapSparql = re.sub(r'(\?|\$){1}' + v + r'\}', value + " } ", jsapSparql, flags=0)

                # replace the variable when it is followed by a dot
                jsapSparql = re.sub(r'(\?|\$){1}' + v + r'\.', value + " . ", jsapSparql, flags=0)

        # return
        return self.nsSparql + jsapSparql
