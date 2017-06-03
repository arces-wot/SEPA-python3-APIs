#!/usr/bin/python3

# global requirements
import os
import sys

# path modification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# local import
from sepy.Consumer import *
from sepy.BasicHandler import *

if __name__ == "__main__":
    
    # configuration files
    jsapFile = "../resources/ExampleProfile.jsap"
    jparFile = "../resources/UserProfile.jpar"
    
    # create a producer
    kp = Consumer(jsapFile, jparFile)

    # produce
    kp.consume("READ_AGE", {}, "age", BasicHandler, False)
