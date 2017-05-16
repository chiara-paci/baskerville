import random,string

def random_string(L=0):
    if not L:
        L=random.choice(list(range(3,50)))
    return ''.join(random.choice(string.lowercase) for x in range(L))

def random_year(ymin=1900,ymax=2017):
    return random.choice(list(range(ymin,ymax)))
