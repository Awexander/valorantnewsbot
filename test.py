list = {'status':404, 'errors':[{'message':'cannot do this'}]}
print(list.get('status'))
print(list.get('errors')[0].get('message'))