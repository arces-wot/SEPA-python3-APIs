#!/usr/bin/python

# global requirements

# local requirements
from .JSAPHandler import *
from .Exceptions import *
from .KP import *


# the Producer
class Producer(KP):

    """The Producer. A simple KP implementing only updates"""

    # constructor
    def __init__(self, sapFile, jparFile):

        """Constructor for the Producer class"""

        # call the superclass constructor
        KP.__init__(self, sapFile, jparFile)
        
        # logger
        self.logger.debug("=== Producer::__init__ invoked ===")


    # produce
    def produce(self, sparqlUpdate, forcedBindings = {}, secure = False):

        """The method to update the Knowledge Base"""

        # retrieve and perform the update
        u = self.jsap.getUpdate(sparqlUpdate, forcedBindings)
        self.kp.update(u, secure) 
