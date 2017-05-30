#!/usr/bin/python3 

# global requirements
import os
import sys
import uuid
import unittest  

# path modification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# local import
from sepy.KP import LowLevelKP

# class
class TestEverything(unittest.TestCase):

    ################################################
    #
    # Tests of the UPDATE functionalities
    #
    ################################################
    
    def test_unsecure_update(self):

        # define a random ID and then a triple
        idd = str(uuid.uuid4())    
        triple = "<%s:%s> <%s:%s> <%s:%s>" % (ns, idd, ns, idd, ns, idd)       

        # create an instance of the KP
        kp = LowLevelKP(conf["host"], conf["queryPath"], conf["registerPath"], conf["tokenPath"], conf["httpPort"], conf["httpsPort"], conf["wsPort"], conf["wssPort"], False, idd, 1000)

        # produce a SPARQL UPDATE to insert data and one to delete it
        s1,r1 = kp.update('INSERT DATA {' + triple + '}')
        s2,r2 = kp.update('DELETE DATA {' + triple + '}')

        # verify the result
        self.assertTrue(s1)
        self.assertTrue(s2)


    # def test_secure_update(self):
    #     self.assertFalse(True)

    # def test_unsecure_query(self):
    #     self.assertFalse(True)

    # def test_secure_query(self):
    #     self.assertFalse(True)

    # def test_notification(self):
    #     self.assertFalse(True)

    # def test_secure_subscribe(self):
    #     self.assertFalse(True)

    # def test_subscribe_confirmed(self):
    #     self.assertFalse(True)

    # def test_secure_unsubscribe(self):
    #     self.assertFalse(True)

    # def test_unsecure_subscribe(self):
    #     self.assertFalse(True)

    # def test_unsecure_unsubscribe(self):
    #     self.assertFalse(True)

    # def test_registration(self):
    #     self.assertFalse(True)

    # def test_multiple_registration(self):
    #     self.assertFalse(True)

    # def test_access_token(self):
    #     self.assertFalse(True)

    # def test_refresh_token(self):
    #     self.assertFalse(True)

    # def test_token_not_expired(self):
    #     self.assertFalse(True)

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
