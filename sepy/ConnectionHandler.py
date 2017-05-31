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
    def __init__(self, host, path, registrationPath, tokenReqPath, # paths
                 httpPort, httpsPort, wsPort, wssPort, # ports
                 clientName): # security

        """Constructor of the ConnectionHandler class"""

        # logger configuration
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== ConnectionHandler::__init__ invoked ===")

        # store parameters as class attributes
        self.httpPort = str(httpPort)
        self.httpsPort = str(httpsPort)
        self.wsPort = str(wsPort)
        self.wssPort = str(wssPort)
        self.host = host
        self.path = path
        self.registrationPath = registrationPath
        self.tokenReqPath = tokenReqPath
        self.clientName = clientName

        # determine complete URIs
        self.queryUpdateURI = "http://" + self.host + ":" + self.httpPort + self.path
        self.queryUpdateURIsecure = "https://" + self.host + ":" + self.httpsPort + self.path
        self.subscribeURI = "ws://" + self.host + ":" + self.wsPort + self.path
        self.subscribeURIsecure = "wss://" + self.host + ":" + self.wssPort + self.path
        self.registerURI = "https://" + self.host + ":" + self.httpsPort + self.registrationPath
        self.tokenReqURI = "https://" + self.host + ":" + self.httpsPort + self.tokenReqPath

        # security data
        self.token = None
        self.clientSecret = None

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
            if not self.clientSecret:
                self.register()
                    
            # if a token is not present, request it!
            if not(self.token):
                self.requestToken()
                
            # perform the request
            self.logger.debug("Performing a secure SPARQL request")
            if isQuery:
                headers = {"Content-Type":"application/sparql-query", 
                           "Accept":"application/json",
                           "Authorization": "Bearer " + self.token}
            else:
                headers = {"Content-Type":"application/sparql-update", 
                           "Accept":"application/json",
                           "Authorization": "Bearer " + self.token}
            r = requests.post(self.queryUpdateURIsecure, headers = headers, data = sparql, verify = False)        
            r.connection.close()
            
            # check for errors on token validity
            if r.status_code == 401:
                self.token = None                
                raise TokenExpiredException

            # return
            return r.status_code, r.text

        # insecure connection 
        else:

            # perform the request
            self.logger.debug("Performing a non-secure SPARQL request")
            if isQuery:
                headers = {"Content-Type":"application/sparql-query", "Accept":"application/json"}
            else:
                headers = {"Content-Type":"application/sparql-update", "Accept":"application/json"}
            r = requests.post(self.queryUpdateURI, headers = headers, data = sparql)
            r.connection.close()
            return r.status_code, r.text


    # do register
    def register(self):

        # debug print
        self.logger.debug("=== ConnectionHandler::register invoked ===")
        
        # define headers and payload
        headers = {"Content-Type":"application/json", "Accept":"application/json"}
        payload = '{"client_identity":' + self.clientName + ', "grant_types":["client_credentials"]}'

        # perform the request
        r = requests.post(self.registerURI, headers = headers, data = payload, verify = False)        
        r.connection.close()
        if r.status_code == 201:
            jresponse = json.loads(r.text)
            cred = base64.b64encode(bytes(jresponse["client_id"] + ":" + jresponse["client_secret"], "utf-8"))
            self.clientSecret = "Basic " + cred.decode("utf-8")
        else:
            raise RegistrationFailedException()


    # do request token
    def requestToken(self):

        # debug print
        self.logger.debug("=== ConnectionHandler::requestToken invoked ===")
        
        # define headers and payload        
        headers = {"Content-Type":"application/json", 
                   "Accept":"application/json",
                   "Authorization": self.clientSecret}    

        # perform the request
        r = requests.post(self.tokenReqURI, headers = headers, verify = False)        
        r.connection.close()
        if r.status_code == 201:
            jresponse = json.loads(r.text)
            self.token = jresponse["access_token"]
        else:
            raise TokenRequestFailedException()


    # do open websocket
    def openWebsocket(self, sparql, alias, handler, secure):                         

        # debug
        self.logger.debug("=== ConnectionHandler::openWebsocket invoked ===")

        # secure?
        if secure:

            # if the client is not yet registered, then register!
            if not self.clientSecret:
                self.register()
                    
            # if a token is not present, request it!
            if not(self.token):
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
                handler.handle()


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
                msg["authorization"] = self.token

            # send subscription request
            ws.send(json.dumps(msg))
            self.logger.debug(msg)


        # configuring the websocket
        if secure:
            ws = websocket.WebSocketApp(self.subscribeURIsecure,
                                        on_message = on_message,
                                        on_error = on_error,
                                        on_close = on_close,
                                        on_open = on_open)                                        
        else:
            ws = websocket.WebSocketApp(self.subscribeURI,
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
        
        
