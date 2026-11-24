"""Functions for specific cases, made for the Clicker Game.
"""

def indent_colons(l):
    """Automatically indent a list with strings with colons at the end.

    Args:
        l (list): a list of str objects with colons at the end.

    Returns:
        List with the items, but with their colons indented to the longest line.

    >>> lines = ["Short:", "Loooooong:", "A:"]
    >>> indent_colons(lines)
    ['Short    :', 'Loooooong:', 'A        :']
    >>> lines = ["AAA:", "BBB:", "CC:"]
    >>> indent_colons(lines)
    ['AAA:', 'BBB:', 'CC :']
    """
    output = []

    ## Assertions
    # Check if all items are strings
    for i in l:
        assert type(i) == str, "All items in the list must be str objects"
    # Check if every item ends with a colon
    for i in l:
        assert i.endswith(":"), "All items in the list must end with a colon (:)"

    # Find the longest item in the list
    long_item_index = 0
    long_item_length = len(l[0])
    for i in range(len(l)):
        if len(l[i]) > long_item_length:
            long_item_index = i
            long_item_length = len(l[i])

    for item in l:
        difference = long_item_length - len(item)
        if difference == 0:
            output.append(item)
            continue
        elif difference < 0:
            raise ValueError
        else:
            output.append(
                item[:-1] + difference * " " + ":"
            )

    return output

def xor_cipher(text, key):
    """Cipher some text with XOR cipher.

    Params:
        - text (str): The text to be ciphered.
        - key  (str): The key to use for ciphering. Cannot be empty.

    Returns:
        - The encrypted text.

    >>> xor_cipher('Hello, world!', 'secret_key')
    ';\x00\x0f\x1e\nX\x7f\x1c\n\x0b\x1f\x01B'
    >>> xor_cipher(';\x00\x0f\x1e\nX\x7f\x1c\n\x0b\x1f\x01B', 'secret_key')
    'Hello, world!'

    >>> xor_cipher('Hello, world!', 424242)
    '|WX^[\x1e\x14E[@XV\x15'
    >>> xor_cipher('|WX^[\x1e\x14E[@XV\x15', 424242)
    'Hello, world!'
    """
    if not key:
        raise ValueError("key must not be empty")
    key = str(key)
    return "".join(
        chr(ord(char) ^ ord(key[i % len(key)]))
        for i, char in enumerate(text)
    )
