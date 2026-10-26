"""Functions to quickly encode to and decode from Base64.

Uses str objects as inputs and outputs str objects directly, rather than going through byte conversion.
The functions do that part for you.

Imports base64's b64decode and b64encode.
"""

from base64 import b64decode, b64encode

__all__ = ["b64_encoded_str", "b64_decoded_str"]

def b64_encoded_str(s: str) -> str:
  """
  Encodes a string in Base64 directly, without needing to use byte objects.
  Takes a str object as its only input.
  Returns the encoded version of the string as a str object.
  """
  tmp = b64encode(s.encode("utf-8"))
  return tmp.decode("utf-8")


def b64_decoded_str(s: str) -> str:
  """
  Decodes a string from Base64 directly, without needing to use byte objects.
  Takes a str object as its only input.
  Returns the decoded version of the string as a str object.
  """
  tmp = b64decode(s.encode("utf-8"))
  return tmp.decode("utf-8")