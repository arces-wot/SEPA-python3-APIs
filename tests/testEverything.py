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
from sepy.JSAPObject import *
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

        # create an instance of the JSAP        
        cls.jsap = JSAPObject(conf["jsapFile"])
        
        # create an instance of the KP
        cls.kp = LowLevelKP(logLevel = 10)

        # create an instance of the secure KP
        cls.skp = LowLevelKP(jparFile = conf["jparFile"], logLevel = 10)
        
        
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
            self.skp.connectionManager.register(self.jsap.registerUri)
        except RegistrationFailedException:
            success = False
        self.assertTrue(success)


    def test_01_multiple_registration(self):

        # debug print
        print(colored("test::01> ", "blue", attrs=["bold"]) + "testing multiple registration")        

        # try a new registation
        exc = False
        try:
            self.skp.connectionManager.register(self.jsap.registerUri)
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
            self.skp.connectionManager.requestToken(self.jsap.tokenReqUri)
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
                s1,r1 = self.skp.query(self.jsap.secureQueryUri, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True, self.jsap.registerUri, self.jsap.tokenReqUri)
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
                s1,r1 = self.skp.query(self.jsap.secureQueryUri, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True, self.jsap.registerUri, self.jsap.tokenReqUri)
            except TokenExpiredException:
                break
                           
        # request a new token
        while True:
            try:
                self.skp.connectionManager.requestToken(self.jsap.tokenReqUri)
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
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (conf["ns"], idd,
                                              conf["ns"], idd,
                                              conf["ns"], idd)       

        # produce a SPARQL UPDATE to insert data and one to delete it
        s1,r1 = self.kp.update(self.jsap.updateUri, 'INSERT DATA {' + triple + '}', False)
        s2,r2 = self.kp.update(self.jsap.updateUri, 'DELETE DATA {' + triple + '}', False)

        # verify the result
        self.assertTrue(s1)
        self.assertTrue(s2)


    def test_06_secure_update(self):

        # debug print
        print(colored("test::06> ", "blue", attrs=["bold"]) + "testing secure update")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (conf["ns"], idd,
                                              conf["ns"], idd,
                                              conf["ns"], idd)       

        # produce a SPARQL UPDATE to insert data and one to delete it
        try:
            s1,r1 = self.skp.update(self.jsap.secureUpdateUri, 'INSERT DATA {' + triple + '}', True, self.jsap.registerUri, self.jsap.tokenReqUri)
        except TokenExpiredException:
            self.kp.connectionManager.requestToken()
            s1,r1 = self.skp.update(self.jsap.secureUpdateUri, 'INSERT DATA {' + triple + '}', True, self.jsap.registerUri, self.jsap.tokenReqUri)

        try:
            s2,r2 = self.skp.update(self.jsap.secureUpdateUri, 'DELETE DATA {' + triple + '}', True, self.jsap.registerUri, self.jsap.tokenReqUri)
        except TokenExpiredException:
            self.kp.connectionManager.requestToken()
            s2,r2 = self.skp.update(self.jsap.secureUpdateUri, 'DELETE DATA {' + triple + '}', True, self.jsap.registerUri, self.jsap.tokenReqUri)

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
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (conf["ns"], idd,
                                              conf["ns"], idd,
                                              conf["ns"], idd)       

        # clear SEPA
        s,r = self.kp.update(self.jsap.queryUri, 'DELETE {?s ?p ?o} WHERE { ?s ?p ?o}', False)

        # produce a SPARQL UPDATE to insert data 
        s,r = self.kp.update(self.jsap.updateUri, 'INSERT DATA {' + triple + '}', False)

        # query data
        s1,r1 = self.kp.query(self.jsap.queryUri, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", False)

        # delete data
        s,r = self.kp.update(self.jsap.updateUri, 'DELETE DATA {' + triple + '}', False)

        # verify the result
        self.assertTrue(s)


    def test_08_secure_query(self):

        # debug print
        print(colored("test::08> ", "blue", attrs=["bold"]) + "testing secure query")        

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (conf["ns"], idd,
                                              conf["ns"], idd,
                                              conf["ns"], idd)       

        # clear SEPA
        s,r = self.kp.update(self.jsap.updateUri, 'DELETE {?s ?p ?o} WHERE { ?s ?p ?o}', False)

        # produce a SPARQL UPDATE to insert data 
        s,r = self.kp.update(self.jsap.updateUri, 'INSERT DATA {' + triple + '}', False)

        # query data
        try:
            s1,r1 = self.skp.query(self.jsap.secureQueryUri, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True, self.jsap.registerUri, self.jsap.tokenReqUri)
        except TokenExpiredException:                                                                  
            self.kp.connectionManager.requestToken(self.jsap.tokenReqUri)
            s1,r1 = self.skp.query(self.jsap.secureQueryUri, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", True, self.jsap.registerUri, self.jsap.tokenReqUri)

        # delete data
        s,r = self.kp.update(self.jsap.updateUri, 'DELETE DATA {' + triple + '}', False)

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
            subid = self.kp.subscribe(self.jsap.subscribeUri, "SELECT ?s WHERE { ?s ?p ?o }", "subjects", None)
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
            subid = self.skp.subscribe(self.jsap.secureSubscribeUri, "SELECT ?s WHERE { ?s ?p ?o }", "subjects", None, True, self.jsap.registerUri, self.jsap.tokenReqUri)
        except:
            success = False
        self.assertTrue(success)


    def test_09_secure_unsubscribe(self):

        success = True
        try:
            global subid
            self.skp.unsubscribe(subid, True)
        except:
            success = False
        self.assertTrue(success)


# main
if __name__ == "__main__":

    # init test configuration
    conf = {}
    conf["ns"] = "http://testNs#"
    conf["jsapFile"] = "example.jsap"
    conf["jparFile"] = "example.jpar"

    # run tests
    unittest.main()
