class invalidJSON(Exception):
    """ Exception raised for invalid JSON files."""
    pass

class invalidPython(Exception):
    """ Exception raised for illegal python files. """
    pass

class illegalImport(Exception):
    """ Exception raised for illegal imports. """
    pass

class illegalCall(Exception):
    """ Exception raised for illegal function calls. """
    pass

class missingFunction(Exception):
    """ Exception raised for missing function call. """
    pass
