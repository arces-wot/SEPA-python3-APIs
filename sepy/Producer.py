#!/usr/bin/python

# global requirements

# local requirements
from .JSAPHandler import *
from .Exceptions import *
from .KP import *


# the Producer
class Producer:

    """The Producer. A simple KP implementing only updates"""

    # constructor
    def __init__(self, sapFile, jparFile):

        """Constructor for the Producer class"""

        # logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== Producer::__init__ invoked ===")

        # create an instance of the JSAPHandler
        self.jsap = JSAPHandler(sapFile)

        # create an instance of the LowLevel KP
        self.kp = LowLevelKP(jparFile, self.jsap)


    # produce
    def produce(self, sparqlUpdate, forcedBindings = {}, secure = False):

        """The method to update the Knowledge Base"""

        # retrieve and perform the update
        u = self.jsap.getUpdate(sparqlUpdate, forcedBindings)
        self.kp.update(u, secure) 
