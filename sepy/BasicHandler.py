#!/usr/bin/python3

# global requirements
import logging


class BasicHandler:

    """A simple example of an Handler class"""
    
    # constructor
    def __init__(self, kp):

        """This is the constructor for the example handler"""

        # get a logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== BasicHandler::__init__ invoked ===")
        
        # store the kp
        self.kp = kp


    # handle notifications
    def handle(self, message):

        # print the notification
        self.logger.debug("=== BasicHandler::handle received the following notification: %s" % message)
