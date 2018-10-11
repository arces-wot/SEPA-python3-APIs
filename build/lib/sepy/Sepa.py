#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Sepa.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
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

from .SEPAClient import *
from .SubscriptionHandler import SubscriptionHandler
import logging

logging.basicConfig(format='%(levelname)s %(asctime)-15s %(message)s',level=logging.INFO)

class DefaultHandler(SubscriptionHandler):
    def __init__(self, kp=None, custom_handler=lambda a,r: None):
        super().__init__(kp=kp)
        self._subHandler = custom_handler
        if kp is None:
            self.logger = logging.getLogger("sepaLogger")
            self.logger.warning("Default logger")
        else:
            self.logger = kp.logger
        
    def handle(self,added,removed):
        hResult = self._subHandler(added,removed)
        if hResult is None:
            self.logger.warning("Default handler called")
            return super().handle(added,removed)
        return hResult

class Sepa:
    """
    This is the High-level class used to develop a client for SEPA.
    """
    def __init__(self,ip="localhost",http_port=8000,ws_port=9000,security={"secure": False, "tokenURI": None, "registerURI": None}):
        """
        ip: where the SEPA is located
        http_port: standard port for query and updates. Default is for unsecure communication.
        ws_port: standard port for subscriptions. Default is for unsecure communication.
        security: dictionary requiring {"secure": False/True, "tokenURI": , "registerURI": }. Default is for unsecure communication
        """
        self.logger = logging.getLogger("sepaLogger")
        self._ip = ip
        self._http_port = http_port
        self._ws_port = ws_port
        self._client = SEPAClient()
        self._security = security
        self._runtime_prefixes = []
        
    def isSecure(self):
        return self._security["secure"]
        
        
    def getIp(self):
        """Getter for ip configuration"""
        return self._ip
        
    def getPort(self):
        """Getter for port configuration"""
        return self._port
        
    def addPrefix(self,label,prefix):
        """Local prefixes that will be used in every communication with sepa using this client"""
        self._runtime_prefixes.append("prefix {}: {}".format(label,prefix))
        
    @property
    def client(self):
        """Getter for the lower level item"""
        return self._client
        
    def set_ip(self,ip):
        """Setter for ip configuration"""
        self._ip = ip
        
    def set_port(self,port):
        """Setter for port configuration"""
        self._port = port
        
    def set_security(self,security):
        """Setter for security configuration"""
        self._security = security
        
    def query(self,sparql,fB={},destination=None):
        """
        Performs a query with the sparql and its forcedBindings;
        Use YSparqlObject to fill the sparql and fB fields.
        If you want to store the output of the query somewhere, use the 'destination' field.
        """
        protocol = "https" if self.isSecure() else "http"
        code,output = self._client.query("{}://{}:{}/query".format(protocol,self._ip,self._http_port),
                            self._bound_sparql(sparql,fB),
                            secure=self._security["secure"],
                            tokenURI=self._security["tokenURI"],
                            registerURI=self._security["registerURI"])
        self.logger.info("Query output code: {}".format(code))
        assert code
        if destination is not None:
            with open(destination,"w") as fileDest:
                print(json.dumps(output),file=fileDest)
        return output
        
    def update(self,sparql,fB={}):
        """
        Performs an update with the sparql and its forcedBindings;
        Use YSparqlObject to fill the sparql and fB fields.
        """
        protocol = "https" if self.isSecure() else "http"
        code,output = self._client.update("{}://{}:{}/update".format(protocol,self._ip,self._http_port),
                                            self._bound_sparql(sparql,fB),
                                            secure=self._security["secure"],
                                            tokenURI=self._security["tokenURI"],
                                            registerURI=self._security["registerURI"])
        self.logger.info("Update output code: {}".format(code))
        assert code
        return output
        
    def _bound_sparql(self,sparql,fB):
        """
        This is a private function that makes the substitution into the SPARQL of the forced
        bindings available.
        The complete SPARQL is returned.
        """
        bSparql = sparql
        for prefix in self._runtime_prefixes:
            if not (prefix in sparql.lower()):
                bSparql = prefix+"\n"+bSparql
        for key in fB.keys():
            if ((fB[key]["type"]=="uri") or (fB[key]["value"]=="UNDEF")):
                bSparql = bSparql.replace("?"+key,fB[key]["value"])
            else:
                bSparql = bSparql.replace("?"+key,"'"+fB[key]["value"]+"'")
        return bSparql

    def subscribe(self,sparql,fB={},alias=None,handler=lambda a,r: None):
        """
        Performs a subscription with the sparql and its forcedBindings;
        Use YSparqlObject to fill the sparql and fB fields.
        You can give an 'alias' to the subscription, as well as an handler. 
        If you don't give the handler, the default null one will be used.
        The subscription id is returned.
        """
        protocol = "wss" if self.isSecure() else "ws"
        return self._client.subscribe("{}://{}:{}/subscribe".format(protocol,self._ip,self._ws_port),
                                        self._bound_sparql(sparql,fB),
                                        alias,
                                        DefaultHandler(kp=self,custom_handler=handler),
                                        secure=self._security["secure"],
                                        tokenURI=self._security["tokenURI"],
                                        registerURI=self._security["registerURI"])
    
    def unsubscribe(self,subid):
        """
        Given the subid, it closes the subscription.
        """
        self._client.unsubscribe(subid,self._security["secure"])
        
    def clear(self):
        """
        Performs a delete where {?a ?b ?c}
        """
        return self.update("delete where {?a ?b ?c}")
        
    def query_all(self):
        """
        Performs a select * where {?a ?b ?c}
        """
        return self.query("select * where {?a ?b ?c}")
