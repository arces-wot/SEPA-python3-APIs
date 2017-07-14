#!/usr/bin/python3

# global requirements

# local requirements
from .Exceptions import *
from .LowLevelKP import *


# the KP
class KP:

    """The KP. A simple KP that must be refined as a
    Producer, Consumer or Aggregator."""

    # constructor
    def __init__(self, jsapFile, jparFile):

        """Constructor for the KP class"""

        # logger
        self.logger = logging.getLogger("sepaLogger")
        self.logger.debug("=== KP::__init__ invoked ===")

        # create an instance of the LowLevel KP
        self.kp = LowLevelKP(jparFile, jsapFile)
