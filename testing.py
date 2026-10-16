# Section 1: exponential growth test
"""
value = 50

f = lambda x, i, m : round(x * (m ** (i ** 0.925)))

for i in range(100):
    print(i, ": ", f(value, i, 1.175), sep = "")
"""

# Section 2: dictionaries in dictionaries
"""
cool_dict = {
    "key1": {
        "key2": "blah blah blah"
    }
}

print(cool_dict)
print(cool_dict["key1"])
print(cool_dict["key1"]["key2"])
"""

# Section 3: help with doc-strings in user-created modules

import weight_mean
help(weight_mean)

import simple_b64
help(simple_b64)