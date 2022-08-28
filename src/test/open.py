import os
SLASH = "\\"
path = os.getcwd()

with open(path +  f"/data/accounts.json", 'r') as w:
    print(w.read())