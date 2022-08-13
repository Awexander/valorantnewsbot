
import json

update = {'test': 'test data', 'second': 'second'}
with open('config/updates.json', 'w') as upjson:
    upjson.write(json.dumps(update, indent=4, separators=[',',':']))