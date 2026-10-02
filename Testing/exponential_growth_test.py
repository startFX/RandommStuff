value = 50

f = lambda x, i, m : round(x * (m ** (i ** 0.925)))

for i in range(100):
    print(i, ": ", f(value, i, 1.175), sep = "")