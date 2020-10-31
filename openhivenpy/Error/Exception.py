# Hiven Exceptions #

class HivenException(Exception):
    pass
    
class InvalidClientType(HivenException):
    pass

class NoDisplayInfo(HivenException):
    pass

class InvalidToken(HivenException):
    pass

class NoneClientType(Warning):
    pass

class UnableToConnect(HivenException):
    pass


# Command Exceptions #

class CommandException(Exception):
    pass #ToDo