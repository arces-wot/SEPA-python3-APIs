#!/usr/bin/python3

class TokenExpiredException(Exception):
    pass

class RegistrationFailedException(Exception):
    pass

class TokenRequestFailedException(Exception):
    pass

class JSAPParsingException(Exception):
    pass

class JPARParsingException(Exception):
    pass

class MissingJPARException(Exception):
    pass

class YSAPParsingException(Exception):
    pass
