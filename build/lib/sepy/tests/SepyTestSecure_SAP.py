#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  SepyTestUnsecure_SAP.py
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

from pkg_resources import resource_filename

import unittest
from collections import defaultdict
from urllib.parse import urlparse

import logging
import yaml
from sepy.SAPObject import SAPObject, generate, YsapTemplate, defaultdict_to_dict
from sepy.SEPA import SEPA
from sepy.tablaze import tablify, check_table_equivalence

EXPECTED_TABLE_test1 = """+----------------------+-----------------+----------------+
|          a           |        b        |       c        |
+----------------------+-----------------+----------------+
| (uri) test:Francesco | (uri) test:dice | (literal) Ciao |
+----------------------+-----------------+----------------+
1 result(s)"""

EXPECTED_TABLE_test2 = """+----------------------+-----------------+
|         nome         |     qualcosa    |
+----------------------+-----------------+
| (uri) test:Francesco |  (literal) Ciao |
|   (uri) test:Fabio   | (literal) Hello |
+----------------------+-----------------+
2 result(s)"""

EXPECTED_TABLE_test3a = """+----------------------+-----------------+
|         nome         |     qualcosa    |
+----------------------+-----------------+
| (uri) test:Francesco |  (literal) Ciao |
|   (uri) test:Fabio   | (literal) Hello |
+----------------------+-----------------+
2 result(s)"""

EXPECTED_TABLE_test3b = """+--------------------+-----------------+
|        nome        |     qualcosa    |
+--------------------+-----------------+
| (uri) test:Adriano | (literal) Salve |
+--------------------+-----------------+
1 result(s)"""


class SepyTestSecure_SAP(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(resource_filename(__name__, "testSecure.ysap"), "r") as sap_file:
            self.ysap = SAPObject(yaml.load(sap_file))
        self.engine = SEPA(sapObject=self.ysap, client_id="TEST-SECURE", logLevel=logging.ERROR)
        self.prefixes = self.ysap.get_namespaces(stringList=True)
    
    def test_0(self):
        parsed_url = urlparse(self.ysap.query_url)
        self.assertEqual(parsed_url.scheme, "https")
        
        parsed_url = urlparse(self.ysap.registration_url)
        self.assertEqual(parsed_url.scheme, "https")
        
        parsed_url = urlparse(self.ysap.registration_url)
        self.assertEqual(parsed_url.scheme, "https")
        
        parsed_url = urlparse(self.ysap.update_url)
        self.assertEqual(parsed_url.scheme, "https")
        
        parsed_url = urlparse(self.ysap.subscribe_url)
        self.assertEqual(parsed_url.scheme, "wss")
    
    def test_1(self):
        self.engine.clear()
            
    def test_2(self):
        self.engine.update("INSERT_GREETING")
        result = self.engine.query_all()

        self.assertEqual(
            tablify(result, prefix_file=self.prefixes, destination=None),
                    EXPECTED_TABLE_test1)
        
    def test_3(self):
        self.assertRaises(
            KeyError, self.engine.update, "INSERT_VARIABLE_GREETING")
        self.engine.update(
            "INSERT_VARIABLE_GREETING",
            forcedBindings={"nome": "test:Fabio", "qualcosa": "Hello"})
        result = self.engine.query("QUERY_GREETINGS")
        self.assertTrue(check_table_equivalence(
            result, EXPECTED_TABLE_test2, self.prefixes))
        
    def test_4(self):
        from threading import Event
        testEvent = Event()
        subid = ""
        notif_counter = 0

        def myHandler(added, removed):
            nonlocal notif_counter
            notif_counter += 1
            addedObject = {}
            addedObject["head"] = {}
            addedObject["head"]["vars"] = list(added[0].keys())
            addedObject["results"] = {}
            addedObject["results"]["bindings"] = added
            if notif_counter == 1:
                self.assertTrue(check_table_equivalence(
                    addedObject, EXPECTED_TABLE_test3a, self.prefixes))
                self.assertEqual(removed, [])
            elif notif_counter == 2:
                self.assertTrue(check_table_equivalence(
                    addedObject, EXPECTED_TABLE_test3b, self.prefixes))
                self.assertEqual(removed, [])
                self.engine.unsubscribe(subid)
                testEvent.set()
        
        subid = self.engine.subscribe(
            "QUERY_GREETINGS", "test", handler=myHandler)
        self.engine.update(
            "INSERT_VARIABLE_GREETING",
            forcedBindings={"nome": "test:Adriano", "qualcosa": "Salve"})
        self.assertTrue(testEvent.wait(timeout=3))
        self.engine.clear()


if __name__ == '__main__':
    unittest.main(failfast=True)