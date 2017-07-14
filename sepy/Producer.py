#!/usr/bin/python

# global requirements

# local requirements
from .Exceptions import *
from .KP import *


# the Producer
class Producer(KP):

    """The Producer. A simple KP implementing only updates"""

    # constructor
    def __init__(self, jsapFile, jparFile, logLevel):

        """Constructor for the Producer class"""

        # call the superclass constructor
        KP.__init__(self, jsapFile, jparFile, logLevel)
        
        # logger
        self.logger.debug("=== Producer::__init__ invoked ===")


    # produce
    def produce(self, sparqlUpdate, forcedBindings = {}, secure = False):

        """The method to update the Knowledge Base"""

        # logger
        self.logger.debug("=== Producer::produce invoked ===")

        # retrieve the update 
        u = self.kp.jsapHandler.getUpdate(sparqlUpdate, forcedBindings)

        # perform the update
        self.kp.update(u, secure) 
