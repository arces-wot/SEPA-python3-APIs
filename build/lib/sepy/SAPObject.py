#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  SAPObject.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from urllib.parse import urlparse

import logging

class SAPObject:
    """
    The SAPObject class unifies the formats of SAP files. The only need
    is to parse the file, and give to the constructor a dictionary built
    as in SEPADocs.
    """
    def __init__(self,parsed_sap_dict):
        """
        Constructor. 
        parsed_sap_dict should be a dictionary.
        """
        self.parsed_sap = parsed_sap_dict
        self.logger = logging.getLogger("sapLogger")
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    def explore(self,path):
        """
        Generic dictionary explorer.
        path is a list of indices to be followed.
        """
        item = None
        try:
            item = self.parsed_sap[path[0]]
            for tag in path[1::]:
                item = item[tag]
        except KeyError as ke:
            self.logger.error(ke)
            return None
        return item
        
    def sparql11protocol(self,path=[]):
        """
        Explorer of the sparql11protocol subobject.
        Use 'path' to get a specific value
        """
        return self.explore(["sparql11protocol"]+path)
        
    def sparql11seprotocol(self,path=[]):
        """
        Explorer of the sparql11seprotocol subobject.
        Use 'path' to get a specific value
        """
        return self.explore(["sparql11seprotocol"]+path)
    
    @staticmethod
    def _url_builder(protocol,ip_address,port,path):
        """
        Builds an url from the parameters.
        """
        return "{}://{}:{}{}".format(protocol,ip_address,port,path)
    
    @property
    def host(self):
        return self.parsed_sap["host"]
        
    @property
    def graphs(self):
        try:
            g = self.parsed_sap["graphs"]
        except KeyError:
            g = {}
        return g
        
    @property
    def registration_url(self):
        return self.explore(["oauth","register"])
        
    @property
    def tokenRequest_url(self):
        return self.explore(["oauth","tokenRequest"])
        
    @property
    def query_url(self):
        return self._url_builder(self.sparql11protocol(path=["protocol"]),
            self.host, self.sparql11protocol(path=["port"]),
            self.sparql11protocol(["query","path"]))
            
    @property
    def update_url(self):
        return self._url_builder(self.sparql11protocol(["protocol"]),
            self.host, self.sparql11protocol(["port"]),
            self.sparql11protocol(["update","path"]))
            
    @property
    def subscribe_url(self):
        use_protocol = self.sparql11seprotocol(["protocol"])
        return self._url_builder(use_protocol,
            self.host, self.sparql11seprotocol(["availableProtocols", use_protocol,"port"]),
            self.sparql11seprotocol(["availableProtocols", use_protocol, "path"]))
            
    @property
    def updates(self):
        """
        Gets the SAP object containing updates. You can access to specific
        updates by using the dict indexes.
        """
        return self.explore(["updates"])
        
    @property
    def queries(self):
        """
        Gets the SAP object containing queries. You can access to specific
        queries by using the dict indexes.
        """
        return self.explore(["queries"])
        
    @staticmethod
    def checkBindings(current,expected):
        """
        This method checks that you give the appropriate forced bindings to the sepa instance.
        In an ysap, the required bindings are the ones that do not have a default value. Which 
        means the ones that have their value == "".
        """
        set_current = set(current.keys())
        set_expected = set(expected.keys())
        # let's take the bindings that are expected from the ysap but not
        # available among those currently given. If one of the expected has value "" (i.e. it is required)
        # an exception is thrown.
        set_difference = set_expected - set_current
        if len(set_difference) != 0:
            for key in set_difference:
                if expected[key]["value"] == "":
                    raise KeyError(key+" is a required forcedbinding")
        return True
    
    @staticmethod
    def sparqlBuilder(unbound_sparql,bindings,namespaces=[]):
        """
        Forced bindings substitution into unbounded SPARQL
        """
        sparql = " ".join(namespaces) + " " + unbound_sparql
        for b in bindings.keys():
            bValue = bindings[b]["value"]
            if bindings[b]["type"] == "literal":
                sparql = sparql.replace("?"+b,"'"+bValue+"'")
            else:
                parseBN_URI = urlparse(bValue)
                if parseBN_URI.scheme == "" or parseBN_URI.netloc == "":
                    sparql = sparql.replace("?"+b,bValue)
                else:
                    sparql = sparql.replace("?"+b,"<"+bValue+">")
        return sparql
    
    def getSparql(self,sparqlSet,identifier,forcedBindings={}):
        """
        Get a sparql from the sap, and performs forced bindings check and
        substitution.
        """
        if "forcedBindings" in sparqlSet[identifier]:
            bindings = sparqlSet[identifier]["forcedBindings"]
            SAPObject.checkBindings(forcedBindings,bindings)
            for b in forcedBindings.keys():
                bindings[b]["value"] = forcedBindings[b]
        else:
            bindings = {}
        return SAPObject.sparqlBuilder(sparqlSet[identifier]["sparql"], 
            bindings,namespaces=self.get_namespaces(stringList=True))
    
    def getUpdate(self,identifier,forcedBindings={}):
        return self.getSparql(self.updates,identifier,forcedBindings)
        
    def getQuery(self,identifier,forcedBindings={}):
        return self.getSparql(self.queries,identifier,forcedBindings)
        
    def get_namespaces(self,stringList=False):
        namespaces = self.explore(["namespaces"])
        if stringList:
            result = []
            for ns, uri in namespaces.items():
                result.append("PREFIX {}: <{}>".format(ns,uri))
            return result
        else:
            return namespaces
