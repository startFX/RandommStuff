from base64 import *

def b64_encoded_str(s):
  """
  Encodes a string in Base64 directly, without needing to use byte objects.
  :param s: The string to encode
  :return: Encoded string as str
  """
  tmp = b64encode(s.encode("utf-8"))
  return tmp.decode("utf-8")


def b64_decoded_str(s):
  """
    Decodes a string from Base64 directly, without needing to use byte objects.
    :param s: The string to decode
    :return: Decoded string as str
    """
  tmp = b64decode(s.encode("utf-8"))
  return tmp.decode("utf-8")