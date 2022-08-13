
import json
import os

path = os.getcwd()
print(path)
with open(path + '/config/updates.json', 'r') as w:
    print(w.read())