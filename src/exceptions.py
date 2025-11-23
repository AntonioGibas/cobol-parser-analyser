class ConfigurationError(Exception):
    pass

class ParsingError(Exception):
    pass

class CobolParsingError(ParsingError):
    pass

class JclParsingError(ParsingError):
    pass

class GraphGenerationError(Exception):
    pass