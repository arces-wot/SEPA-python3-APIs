#!/usr/bin/python3

import re
import yaml
import logging
from .Exceptions import *

class YSAPObject:

    """
    The class to read YSAP files (YAML Semantic Application Profile).


    Parameters
    ----------
    YSAPFile : str
        The name (with relative or absolute path) of the YSAP file
    logLevel : int
        The desired level of debugging information (default = 40)

    Attributes
    ----------
    ysap : dict
        The full dictionary with the YSAP content
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

    """
    
    def __init__(self, YSAPFile, logLevel = 40):

        """
        The constructor of the YSAPObject class. 

        Parameters
        ----------
        YSAPFile : str
            The name (with relative or absolute path) of the YSAP file
        logLevel : int
            The desired level of debugging information (default = 40)

        """
        
        # logger
        self.logger = logging.getLogger("sepaLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.setLevel(logLevel)
        self.logger.debug("=== JSAPObject::__init__ invoked ===")
        
        # try to open YSAP file
        self.logger.debug("Opening YSAP file")
        try:
            self.ysap = yaml.load(open(YSAPFile, "r"))
        except FileNotFoundError:
            raise YSAPParsingException("File not found!")

        # read URIs
        self.logger.debug("Reading URIs")
        try:
            self.updateURI = "http://%s:%s%s" % (self.ysap["parameters"]["host"],
                                                 self.ysap["parameters"]["ports"]["http"],
                                                 self.ysap["parameters"]["paths"]["update"])
            self.queryURI = "http://%s:%s%s" % (self.ysap["parameters"]["host"],
                                                self.ysap["parameters"]["ports"]["http"],
                                                self.ysap["parameters"]["paths"]["query"])
            self.subscribeURI = "ws://%s:%s%s" % (self.ysap["parameters"]["host"],
                                                  self.ysap["parameters"]["ports"]["ws"],
                                                  self.ysap["parameters"]["paths"]["subscribe"])
        except KeyError:
            raise YSAPParsingException("Wrong URI configuration")
        
        # read namespaces
        self.logger.debug("Reading namespaces")
        try:
            self.namespaces = {}
            for ns in self.ysap["namespaces"]:
                self.namespaces[ns] = self.ysap["namespaces"][ns]
                
        except Exception as e:
            raise YSAPParsingException("Error with namespace configuration")            
            
        # read queries
        self.logger.debug("Reading queries")
        try:
            self.queries = {}
            for q in self.ysap["queries"]:
                self.queries[q] = self.ysap["queries"][q]["sparql"]                
        except Exception as e:
            raise YSAPParsingException("Error with queries configuration")
            
        # read updates
        self.logger.debug("Reading updates")
        try:
            self.updates = {}
            for u in self.ysap["updates"]:
                self.updates[u] = self.ysap["updates"][u]["sparql"]                
        except Exception as e:
            raise YSAPParsingException("Error with updates configuration")
        

    def getUpdate(self, uName, forcedBindings):

        """
        Returns a SPARQL update retrieved from the YSAP and
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        uName : str
            The friendly name of the SPARQL Update
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template

        Returns
        -------
        str
            The complete SPARQL Update
        
        """

        self.logger.debug("Retrieving SPARQL Update %s" % uName)
        return self.getSPARQL(uName, forcedBindings, False)

    
    def getQuery(self, qName, forcedBindings):

        """
        Returns a SPARQL query retrieved from the YSAP and
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        qName : str
            The friendly name of the SPARQL Query
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template

        Returns
        -------
        str
            The complete SPARQL Query
       
        """

        self.logger.debug("Retrieving SPARQL Query %s" % qName)
        return self.getSPARQL(qName, forcedBindings, True)

    
    def getSPARQL(self, name, forcedBindings, isQuery):

        """
        Returns a SPARQL query/update retrieved from the YSAP and 
        modified with the forced bindings provided by the user.

        Parameters
        ----------
        uName : str
            The friendly name of the SPARQL Update
        forcedBindings : Dict
            The dictionary containing the bindings to fill the template
        isQuery : bool
            A variable to specify if looking for a query or an update

        Returns
        -------
        str
            The complete SPARQL Query or Update
        
        """
        
        try:

            # get the query/update
            sparqlText = None
            if isQuery:
                sparqlText = self.queries[name]
            else:
                sparqlText = self.updates[name]

            # apply forced bindings
            for v in forcedBindings.keys():
                
                # determine the variable replacement
                value = forcedBindings[v]
                
                # replace the variable when it is followed by a space
                sparqlText = re.sub(r'(\?|\$){1}' + v + r'\s+', value + " ", sparqlText, flags=0)
                
                # replace the variable when it is followed by a braket
                sparqlText = re.sub(r'(\?|\$){1}' + v + r'\}', value + " } ", sparqlText, flags=0)
                
                # replace the variable when it is followed by a dot
                sparqlText = re.sub(r'(\?|\$){1}' + v + r'\.', value + " . ", sparqlText, flags=0)

            # return!
            return sparqlText
            
        # catch errors if query/update does not exist
        except KeyError:
            raise YSAPParsingException("SPARQL Query/Update not found!")

    
    def getNamespace(self, ns):

        """
        Returns a namespace, given its prefix.

        Parameters
        ----------
        ns : str
            The prefix bound to the namespace

        Returns
        -------
        str
            The namespace bound to that prefix

        """

        self.logger.debug("Retrieving namespace for prefix %s" % ns)
        try:
            return self.namespaces[ns]
        except KeyError:
            raise YSAPParsingException("Namespace not found!")
