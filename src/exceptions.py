class VariableNotSetException(Exception):
    """Exception raised for missing variables.

    Attributes:
        variable -- environment variable which is missing
        message -- explanation of the error.    
    """
    def __init__(self, variable, message="Environment Variable not set: "):
        self.variable = variable
        self.message = message
        super().__init__(self.message)

class ConnectionException(Exception):
    """Exception raised for Connection Error.

    Attributes:
        url -- url with connection error
        message -- explanation of the error.    
    """

    def __init__(self, url, message="Error when connecting to URL: "):
        self.url = url
        self.message = message
        super().__init__(self.message)
