#!/usr/bin/python3

# global requirements
import threading
import websocket
import requests
import asyncio
import logging
import base64
import time
import json
import sys
import ssl

# local requirements
from .Exceptions import *

# class ConnectionHandler
class ConnectionHandler:

    """This is the ConnectionHandler class"""

    # constructor
    def __init__(self, jparHandler, jsapHandler = None):

        """Constructor of the ConnectionHandler class"""

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== ConnectionHandler::__init__ invoked ===")

        # store the JPAR and JSAP Handlers
        self.jparHandler = jparHandler
        self.jsapHandler = jsapHandler

        # determine URIs
        if jsapHandler:
            self.queryURI = jsapHandler.queryURI
            self.updateURI = jsapHandler.updateURI
            self.queryURIsec = jsapHandler.queryURIsec
            self.updateURIsec = jsapHandler.updateURIsec
            self.subscribeURI = jsapHandler.subscribeURI
            self.subscribeURIsec = jsapHandler.subscribeURIsec
            self.registerURI = jsapHandler.registerURI
            self.getTokenURI = jsapHandler.getTokenURI
        else:
            self.queryURI = jparHandler.queryURI
            self.updateURI = jparHandler.updateURI
            self.queryURIsec = jparHandler.queryURIsec
            self.updateURIsec = jparHandler.updateURIsec
            self.subscribeURI = jparHandler.subscribeURI
            self.subscribeURIsec = jparHandler.subscribeURIsec
            self.registerURI = jparHandler.registerURI
            self.getTokenURI = jparHandler.getTokenURI

        # open subscriptions
        self.websockets = {}


    # do HTTP request
    def request(self, sparql, isQuery, secure):

        """Method to issue a SPARQL request over HTTP(S)"""

        # debug
        self.logger.debug("=== ConnectionHandler::request invoked ===")
        
        # if security is needed
        if secure:

            # if the client is not yet registered, then register!
            if not self.jparHandler.client_secret:
                self.register()
                    
            # if a token is not present, request it!
            if not(self.jparHandler.jwt):
                self.requestToken()
                
            # perform the request
            self.logger.debug("Performing a secure SPARQL request")
            if isQuery:
                headers = {"Content-Type":"application/sparql-query", 
                           "Accept":"application/json",
                           "Authorization": "Bearer " + self.jparHandler.jwt}
                r = requests.post(self.queryURIsec, headers = headers, data = sparql, verify = False)        
                r.connection.close()
            else:
                headers = {"Content-Type":"application/sparql-update", 
                           "Accept":"application/json",
                           "Authorization": "Bearer " + self.jparHandler.jwt}
                r = requests.post(self.updateURIsec, headers = headers, data = sparql, verify = False)        
                r.connection.close()
            
            # check for errors on token validity
            if r.status_code == 401:
                self.jparHandler.jwt = None                
                raise TokenExpiredException

            # return
            return r.status_code, r.text

        # insecure connection 
        else:

            # perform the request
            self.logger.debug("Performing a non-secure SPARQL request")
            if isQuery:
                headers = {"Content-Type":"application/sparql-query", "Accept":"application/json"}
                r = requests.post(self.queryURI, headers = headers, data = sparql)
                r.connection.close()
            else:
                headers = {"Content-Type":"application/sparql-update", "Accept":"application/json"}
                r = requests.post(self.updateURI, headers = headers, data = sparql)
                r.connection.close()
            return r.status_code, r.text


    ###################################################
    #
    # registration function
    #
    ###################################################

    def register(self):

        # debug print
        self.logger.debug("=== ConnectionHandler::register invoked ===")
        
        # define headers and payload
        headers = {"Content-Type":"application/json", "Accept":"application/json"}
        payload = '{"client_identity":' + self.jparHandler.client_name + ', "grant_types":["client_credentials"]}'

        # perform the request
        r = requests.post(self.registerURI, headers = headers, data = payload, verify = False)        
        r.connection.close()
        if r.status_code == 201:

            # parse the response
            jresponse = json.loads(r.text)

            # encode with base64 client_id and client_secret
            cred = base64.b64encode(bytes(jresponse["client_id"] + ":" + jresponse["client_secret"], "utf-8"))
            self.jparHandler.client_secret = "Basic " + cred.decode("utf-8")
            
            # store data into the jpar file
            self.jparHandler.storeConfig()

        else:
            raise RegistrationFailedException()


    ###################################################
    #
    # token request
    #
    ###################################################

    # do request token
    def requestToken(self):

        # debug print
        self.logger.debug("=== ConnectionHandler::requestToken invoked ===")
        
        # define headers and payload        
        headers = {"Content-Type":"application/json", 
                   "Accept":"application/json",
                   "Authorization": self.jparHandler.client_secret}    

        # perform the request
        r = requests.post(self.getTokenURI, headers = headers, verify = False)        
        r.connection.close()
        if r.status_code == 201:
            jresponse = json.loads(r.text)
            self.jparHandler.jwt = jresponse["access_token"]
        else:
            raise TokenRequestFailedException()


    ###################################################
    #
    # websocket section
    #
    ###################################################

    # do open websocket
    def openWebsocket(self, sparql, alias, handler, secure):                         

        # debug
        self.logger.debug("=== ConnectionHandler::openWebsocket invoked ===")

        # secure?
        if secure:

            # if the client is not yet registered, then register!
            if not self.jparHandler.client_secret:
                self.register()
                    
            # if a token is not present, request it!
            if not(self.jparHandler.jwt):
                self.requestToken()

        # initialization
        handler = handler
        subid = None

        # on_message callback
        def on_message(ws, message):

            # debug
            self.logger.debug("=== ConnectionHandler::on_message invoked ===")
            self.logger.debug(message)

            # process message
            jmessage = json.loads(message)
            if "subscribed" in jmessage:

                # get the subid
                nonlocal subid
                subid = jmessage["subscribed"]
                self.logger.debug("SUBID = " + subid)

                # save the subscription id and the thread
                self.websockets[subid] = ws

            elif "ping" in jmessage:                
                pass # we ignore ping

            else:

                # debug print
                self.logger.debug("Received: " + message)

                # invoke the handler
                handler.handle(message)


        # on_error callback
        def on_error(ws, error):

            # debug
            self.logger.debug("=== ConnectionHandler::on_error invoked ===")


        # on_close callback
        def on_close(ws):

            # debug
            self.logger.debug("=== ConnectionHandler::on_close invoked ===")

            # destroy the websocket dictionary
            del self.websockets[subid]


        # on_open callback
        def on_open(ws):           

            # debug
            self.logger.debug("=== ConnectionHandler::on_open invoked ===")

            # composing message
            msg = {}
            msg["subscribe"] = sparql
            msg["alias"] = alias
            if secure:
                msg["authorization"] = self.jparHandler.jwt

            # send subscription request
            ws.send(json.dumps(msg))
            self.logger.debug(msg)


        # configuring the websocket        
        ws = websocket.WebSocketApp((self.subscribeURIsec if (secure) else self.subscribeURI),
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close,
                                    on_open = on_open)                                        

        # starting the websocket thread
        if secure:
            wst = threading.Thread(target=ws.run_forever, kwargs=dict(sslopt={"cert_reqs": ssl.CERT_NONE}))
        else:
            wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        # return
        while not subid:
            self.logger.debug("Waiting for subscription ID")
            time.sleep(0.1)            
        return subid


    def closeWebsocket(self, subid, secure):

        # debug
        self.logger.debug("=== ConnectionHandler::closeWebSocket invoked ===")

        # retrieve the subscription, close it and delete it
        self.websockets[subid].close()
        del self.websockets[subid]
        
        
