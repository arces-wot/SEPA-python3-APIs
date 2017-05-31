#!/usr/bin/python3 

# global requirements
import os
import sys
import time
import uuid
import unittest  
from termcolor import colored

# path modification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# local import
from sepy.KP import LowLevelKP
from sepy.Exceptions import *

# global variables
subid = None

# class
class TestEverything(unittest.TestCase):

    ################################################
    #
    # Initialization
    #
    ################################################

    @classmethod
    def setUpClass(cls):
        
        # debug print
        print(colored("test::setUpClass> ", "blue", attrs=["bold"]) + "Initializing environment")
        
        # create an instance of the KP
        cls.kp = LowLevelKP(conf["host"], conf["queryPath"], conf["registerPath"], conf["tokenPath"], conf["httpPort"], conf["httpsPort"], conf["wsPort"], conf["wssPort"], "TestUser", 110)
        

    ################################################
    #
    # Tests about Registration
    #
    ################################################
        
    def test_00_registration(self):

        # debug print
        print(colored("test::00> ", "blue", attrs=["bold"]) + "testing registration")        

        success = True
        try:
            self.kp.connectionManager.register()
        except RegistrationFailedException:
            success = False
        self.assertTrue(success)


    def test_01_multiple_registration(self):

        # debug print
        print(colored("test::01> ", "blue", attrs=["bold"]) + "testing multiple registration")        

        # try a new registation
        exc = False
        try:
            self.kp.connectionManager.register()
        except RegistrationFailedException:
            exc = True
        self.assertTrue(exc)


    ################################################
    #
    # Tests about Tokens
    #
    ################################################    

    def test_02_get_access_token(self):

        # debug print
        print(colored("test::02> ", "blue", attrs=["bold"]) + "testing token request")        

        # initialize the exit status
        success = True
        
        # get a token
        try:
            self.kp.connectionManager.requestToken()
        except TokenRequestFailedException:
            success = False
            
        # verify the result
        self.assertTrue(success)


    def test_03_token_expired(self):

        # debug print
        print(colored("test::03> ", "blue", attrs=["bold"]) + "testing token expiry")    

        # wait for an eventual token to expire      
        success = False
        while not(success):
            try:
                s1,r1 = self.kp.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True)
                time.sleep(1)
            except TokenExpiredException:
                success = True
                break
                
        # check the result
        self.assertTrue(success)


    def test_04_refresh_token(self):

        # debug print
        print(colored("test::04> ", "blue", attrs=["bold"]) + "testing token refresh")        

        # initialize the exit status
        success = True
        
        # wait until token expires
        while True:
            time.sleep(1)
            try:
                s1,r1 = self.kp.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True)
            except TokenExpiredException:
                break
                           
        # request a new token
        while True:
            try:
                self.kp.connectionManager.requestToken()
                success = True
                break
            except TokenRequestFailedException:                
                success = False

        # verify the result
        self.assertTrue(success)


    ################################################
    #
    # Tests of the UPDATE functionalities
    #
    ################################################
    
    def test_05_unsecure_update(self):

        # debug print
        print(colored("test::05> ", "blue", attrs=["bold"]) + "testing unsecure update")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (ns, idd, ns, idd, ns, idd)       

        # produce a SPARQL UPDATE to insert data and one to delete it
        s1,r1 = self.kp.update('INSERT DATA {' + triple + '}', False)
        s2,r2 = self.kp.update('DELETE DATA {' + triple + '}', False)

        # verify the result
        self.assertTrue(s1)
        self.assertTrue(s2)


    def test_06_secure_update(self):

        # debug print
        print(colored("test::06> ", "blue", attrs=["bold"]) + "testing secure update")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (ns, idd, ns, idd, ns, idd)       

        # produce a SPARQL UPDATE to insert data and one to delete it
        try:
            s1,r1 = self.kp.update('INSERT DATA {' + triple + '}', True)
        except TokenExpiredException:
            self.kp.connectionManager.requestToken()
            s1,r1 = self.kp.update('INSERT DATA {' + triple + '}', True)

        try:
            s2,r2 = self.kp.update('DELETE DATA {' + triple + '}', True)
        except TokenExpiredException:
            self.kp.connectionManager.requestToken()
            s2,r2 = self.kp.update('DELETE DATA {' + triple + '}', True)

        # verify the result
        self.assertTrue(s1)
        self.assertTrue(s2)


    ################################################
    #
    # Tests of the QUERY functionalities
    #
    ################################################

    def test_07_unsecure_query(self):

        # debug print
        print(colored("test::07> ", "blue", attrs=["bold"]) + "testing unsecure query")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (ns, idd, ns, idd, ns, idd)       

        # clear SEPA
        s,r = self.kp.update('DELETE {?s ?p ?o} WHERE { ?s ?p ?o}', False)

        # produce a SPARQL UPDATE to insert data 
        s,r = self.kp.update('INSERT DATA {' + triple + '}', False)

        # query data
        s1,r1 = self.kp.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }", False)

        # delete data
        s,r = self.kp.update('DELETE DATA {' + triple + '}', False)

        # verify the result
        self.assertTrue(s)


    def test_08_secure_query(self):

        # debug print
        print(colored("test::08> ", "blue", attrs=["bold"]) + "testing secure query")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (ns, idd, ns, idd, ns, idd)       

        # clear SEPA
        s,r = self.kp.update('DELETE {?s ?p ?o} WHERE { ?s ?p ?o}', False)

        # produce a SPARQL UPDATE to insert data 
        s,r = self.kp.update('INSERT DATA {' + triple + '}', False)

        # query data
        try:
            s1,r1 = self.kp.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True)
        except TokenExpiredException:
            self.kp.connectionManager.requestToken()
            s1,r1 = self.kp.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True)

        # delete data
        s,r = self.kp.update('DELETE DATA {' + triple + '}', False)

        # verify the result
        self.assertTrue(s1)


    ################################################
    #
    # Tests of the SUBSCRIBE functionalities
    #
    ################################################

    def test_09_unsecure_subscribe(self):

        # debug print
        print(colored("test::09> ", "blue", attrs=["bold"]) + "testing unsecure subscribe")        

        success = True
        try:
            global subid
            subid = self.kp.subscribe("SELECT ?s WHERE { ?s ?p ?o }", "subjects", None, False)
        except:
            success = False
        self.assertTrue(success)


    def test_10_unsecure_unsubscribe(self):

        # debug print
        print(colored("test::10> ", "blue", attrs=["bold"]) + "testing unsecure unsubscribe")        

        success = True
        try:
            global subid
            self.kp.unsubscribe(subid, False)
        except:
            success = False
        self.assertTrue(success)


    def test_08_secure_subscribe(self):

        success = True
        try:
            global subid
            subid = self.kp.subscribe("SELECT ?s WHERE { ?s ?p ?o }", "subjects", None, True)
        except:
            success = False
        self.assertTrue(success)


    def test_09_secure_unsubscribe(self):

        success = True
        global subid
        self.kp.unsubscribe(subid, True)


# main
if __name__ == "__main__":
    
    # define conf
    ns = "http://testNs#"
    conf = {}

    # define URI parts
    conf["host"] = "localhost"
    conf["subPath"] = "/sparql"
    conf["queryPath"] = "/sparql"
    conf["updatePath"] = "/sparql"
    conf["tokenPath"] = "/oauth/token"
    conf["registerPath"] = "/oauth/register"
    conf["httpPort"] = 8000
    conf["httpsPort"] = 8443
    conf["wsPort"] = 9000
    conf["wssPort"] = 9443
    
    # define URIs
    conf["updateURI"] = "http://%s:%s/%s" % (conf["host"], conf["httpPort"], conf["updatePath"])
    conf["updateURIsecure"] = "https://%s:%s/%s" % (conf["host"], conf["httpsPort"], conf["updatePath"])
    conf["queryURI"] = "http://%s:%s/%s" % (conf["host"], conf["httpPort"], conf["queryPath"])
    conf["queryURIsecure"] = "https://%s:%s/%s" % (conf["host"], conf["httpsPort"], conf["queryPath"])
    conf["subscribeURI"] = "ws://%s:%s/%s" % (conf["host"], conf["wsPort"], conf["subPath"])
    conf["subscribeURI"] = "ws://%s:%s/%s" % (conf["host"], conf["wssPort"], conf["subPath"])
    conf["tokenURI"] = "https://%s:%s/%s" % (conf["host"], conf["httpsPort"], conf["tokenPath"])
    conf["registrationURI"] = "https://%s:%s/%s" % (conf["host"], conf["httpsPort"], conf["registerPath"])

    # run tests
    unittest.main()
