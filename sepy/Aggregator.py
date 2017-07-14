#!/usr/bin/python

# global requirements

# local requirements
from .Exceptions import *
from .KP import *


# the Aggregator
class Aggregator(KP):

    # constructor
    def __init__(self, jsapFile, jparFile):

        """Constructor of the Aggregator class"""

        # call the superclass constructor
        KP.__init__(self, jsapFile, jparFile)

        # logger
        self.logger.debug("=== Aggregator::__init__ invoked ===")

        
    # aggregate
    def aggregate(self, sparqlQuery, forcedBindings, queryAlias, handlerClass, secure = False):

        """This is the most important method of the class:
        it allows to subscribe to the context broker and bind
        an handler class to the subscription"""

        # logger
        self.logger.debug("=== Aggregator::aggregate invoked ===")

        # get the query from the jsap file
        query = self.kp.jsapHandler.getQuery(sparqlQuery, forcedBindings)

        # subscribe
        self.kp.subscribe(query, queryAlias, handlerClass(self.kp), secure)        
