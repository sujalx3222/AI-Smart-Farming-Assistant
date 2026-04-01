from rest_framework.parsers import JSONParser

class PlainTextJSONParser(JSONParser):
    """
    Custom parser to handle requests with Content-Type: text/plain
    but containing JSON data. This is helpful for manual testing
    or clients that don't correctly set the Content-Type header.
    """
    media_type = 'text/plain'
