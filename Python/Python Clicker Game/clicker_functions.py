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