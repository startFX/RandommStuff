"""
Utility functions for calculating weighted averages.
"""

def weight_mean_lists(values, weights):
    """
    Calculates a weighted average with two lists as arguments:
        - values: the values
        - weights: the values' weights
    Returns a float.

    Usage example:
    >>> v = [20, 15, 12]
    >>> w = [1, 2, 0.5]
    >>> weight_mean_lists(v, w)
    13.428571428571429
    """
    assert len(values) == len(weights), "The two lists' lengths must be the same"
    assert values != [], "Values list cannot be empty"
    assert weights != [], "Weights list cannot be empty"
    total = 0.0 ; total_weight = 0.0
    for i in range(len(values)):
        total += values[i]
        total_weight += weights[i]
    return total / total_weight

def weight_mean_2d(values):
    """
    Calculates a weighted average with a list as argument:
        - values: a list containing lists. Each item is another list containing two values: the value itself and its weight. Here's an example:
            >>> ex = [[20, 1], [15, 2], [12, 0.5]]
            So, here, the 20 has a weight of 1, 15 a weight of 2, 12 a weight of 0.5.
    Returns a float.

    Usage example:
    >>> v = [[20, 1], [15, 2], [12, 0.5]]
    >>> weight_mean_2d(v)
    13.428571428571429
    """
    for i in values:
        assert len(i) == 2, "Value list items must have two items"
    assert values != [], "Values list cannot be empty"
    total = 0.0 ; total_weight = 0.0
    for i in values:
        total += i[0]
        total_weight += i[1]
    return total / total_weight