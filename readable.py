import pickle
import pprint

with open("database.p", "rb") as FILE:
    pprint.pprint(pickle.load(FILE))

