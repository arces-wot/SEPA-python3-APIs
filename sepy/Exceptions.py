#!/usr/bin/python3

class TokenExpiredException(Exception):
    pass

class RegistrationFailedException(Exception):
    pass

class TokenRequestFailedException(Exception):
    pass

class SapParsingException(Exception):
    pass

class JPARParsingException(Exception):
    pass
