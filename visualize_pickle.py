import pickle
from pprint import pprint
with open("encodings.pickle",'rb') as f:
    # print(pickle.loads(f.read()))
    # print(pickle.loads(f.read())[0])
    pprint(pickle.loads(f.read())[1])