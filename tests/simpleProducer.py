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
from sepy.Producer import *

if __name__ == "__main__":
    
    # configuration files
    jsapFile = "../resources/ExampleProfile.jsap"
    jparFile = "../resources/UserProfile.jpar"
    
    # create a producer
    kp = Producer(jsapFile, jparFile)

    # produce
    kp.produce("INSERT_FOO", {"age":25})
