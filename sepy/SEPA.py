#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  SEPA.py
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

from SAPObject import SAPObject
from ConnectionHandler import *

import logging
import json

class SEPA:    
    def __init__(self,sapObject=None,logLevel=40):
        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        self.logger.setLevel(logLevel)
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logLevel)
        self.logger.debug("=== SEPA::__init__ invoked ===")
        
        # initialize data structures
        self.sap = sapObject
        self.connectionManager = ConnectionHandler(logLevel=logLevel)
        
    def get_subscriptions(self):
        return self.connectionManager.get_subscriptions()
        
    def setSAP(self,sapObject):
        self.sap = sapObject
        
    def query(self,sapIdentifier,forcedBindings={},destination=None,host=None,token_url=None,register_url=None):
        """
        Performs a query with the sap entry tag;
        If you want to store the output of the query somewhere, use the 'destination' field.
        """
        sparql = self.sap.getQuery(sapIdentifier,forcedBindings)
        return self.sparql_query(sparql, destination=destination, host=host,
            token_url=token_url, register_url=register_url)

        
    def sparql_query(self,sparql,destination=None,host=None,token_url=None,register_url=None):
        """
        Performs a query with the sparql and its forcedBindings;
        If you want to store the output of the query somewhere, use the 'destination' field.
        """
        # perform the query request
        sepa_host = self.sap.query_url if (host is None) else host
        if "https://" in sepa_host:
            sepa_token = self.sap.tokenRequest_url if (token_url is None) else token_url
            sepa_register = self.sap.registration_url if (register_url is None) else register_url
            status, results = self.connectionManager.secureRequest(sepa_host, 
                sparql, True, sepa_token, sepa_register)
        else:
            status, results = self.connectionManager.unsecureRequest(sepa_host, sparql, True)
        if int(status) == 200:
            jresults = json.loads(results)
            if "error" in jresults:
                self.logger.error(jresults["error"]["message"])
                raise
            elif destination is not None:
                with open(destination,"w") as fileDest:
                    print(json.dumps(jresults),file=fileDest)
            return jresults
        else:
            self.logger.error("Query status code: {}".format(status))
            raise
        
    def update(self,sapIdentifier,forcedBindings={},host=None,token_url=None,register_url=None):
        """
        Performs an update with the sap entry tag;
        """
        sparql = self.sap.getUpdate(sapIdentifier,forcedBindings)
        return self.sparql_update(sparql, host=host, token_url=token_url, 
            register_url=register_url)
        
    def sparql_update(self,sparql,host=None,token_url=None,register_url=None):
        """
        Performs an update with the sparql and its forcedBindings;
        """
        # perform the update request
        sepa_host = self.sap.update_url if (host is None) else host
        if "https://" in sepa_host:
            sepa_token = self.sap.tokenRequest_url if (token_url is None) else token_url
            sepa_register = self.sap.registration_url if (register_url is None) else register_url
            status, results = self.connectionManager.secureRequest(sepa_host, 
                sparql, False, sepa_token, sepa_register)
        else:
            status, results = self.connectionManager.unsecureRequest(sepa_host, sparql, False)
        # return
        if int(status) == 200:
            return results
        else:
            self.logger.error(results)
            raise
        
    def clear(self,host=None,token_url=None,register_url=None):
        """
        Performs a delete where {?a ?b ?c}
        """
        return self.sparql_update("delete where {?a ?b ?c}", host=host, 
            token_url=token_url, register_url=register_url)
        
    def query_all(self,host=None,token_url=None,register_url=None):
        """
        Performs a select * where {?a ?b ?c}
        """
        return self.sparql_query("select * where {?a ?b ?c}", host=host, 
            token_url=token_url, register_url=register_url)
        
    def sparql_subscribe(self,sparql,alias,handler=lambda a,r: None,host=None,token_url=None,register_url=None, default_graph=None, named_graph=None):
        subid = None
        sepa_host = self.sap.subscribe_url if (host is None) else host
        if (default_graph is not None) or ("default-graph-uri" not in self.sap.graphs.keys()):
            def_graph = default_graph
        else:
            def_graph = self.sap.graphs["default-graph-uri"]
        if (named_graph is not None) or ("named-graph-uri" not in self.sap.graphs.keys()):
            nam_graph = named_graph
        else:
            nam_graph = self.sap.graphs["named-graph-uri"]
        if "wss://" in sepa_host:
            sepa_token = self.sap.tokenRequest_url if (token_url is None) else token_url
            sepa_register = self.sap.registration_url if (register_url is None) else register_url
            subid = self.connectionManager.openSecureWebsocket(sepa_host, 
                sparql, alias, handler, sepa_register, sepa_token)
        else:
            subid = self.connectionManager.openUnsecureWebsocket(sepa_host, 
                sparql, alias, handler, default_graph=def_graph, named_graph=nam_graph)
        return subid
        
    def subscribe(self,sapIdentifier,alias,forcedBindings={},handler=lambda a,r: None,host=None,token_url=None,register_url=None, default_graph=None, named_graph=None):
        """
        Performs a subscription with the sap identifier tag and its forcedBindings;
        You can give an 'alias' to the subscription, as well as an handler. 
        If you don't give the handler, the default null one will be used.
        The subscription id is returned.
        """
        sparql = self.sap.getQuery(sapIdentifier,forcedBindings)
        return self.sparql_subscribe(sparql, alias, handler, host=host, 
            token_url=token_url, register_url=register_url, 
            default_graph=default_graph, named_graph=named_graph)
        
    def unsubscribe(self,subid):
        # close the subscription, given the id
        self.connectionManager.closeWebsocket(subid)
