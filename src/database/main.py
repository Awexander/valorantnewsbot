
from mysql import mysql
from config import basedata
import os
import json

class database:
    def __init__(self):
        self.db = mysql()

def update_matchtable(self, matches, tableName):
    #get players column
    
    path = os.getcwd() + "/data/"
    with open(path + f"{matches}.json", 'r') as r:
        matchreport = json.loads(r.read())
    
    matchid = matchreport.get('matchid')
    mapName = matchreport.get('map')
    time = matchreport.get('timeplayed')
    mode = matchreport.get('gamemode')
    red = matchreport.get('result').get('red')
    blue = matchreport.get('result').get('blue')
    players = matchreport.get('players')

    #update matchlist first before update individual match
    self.db.insert(  fromtable=basedata.matchlist, 
                select= basedata.matchlist_select, 
                values=(matchid, 
                        mapName,
                        red,
                        blue,
                        mode, 
                        time, 
                    )
                )

    #insert players details and report into new table
    
    for player in players:
        self.db.insert(fromtable=tableName,
                    select=basedata.match_select,
                    values=(player.get('puuid'),
                            player.get('name'),
                            player.get('tag'),
                            player.get('team'),
                            player.get('rank'),
                            player.get('agent'),
                            player.get('acs'),
                            player.get('headshot'),
                            player.get('kda')[3],
                            player.get('kda')[0],
                            player.get('kda')[1],
                            player.get('kda')[2],
                            player.get('adr')
                            )
                    )
def getmatchid(self):
    path = os.getcwd() + "/data/"
    matches = [f[:-5] for f in os.listdir(path) if f[-5:] == ".json"]
    matchid = []
    for match in matches:
        tableName = "match_" + _parse_matchid(match)
        matchid.append(tableName)
        
        if tableName in [table for table in self.db.tables()]:   
            self.db.run(f"DELETE FROM {basedata.matchlist} WHERE matchid='{match}';")
            deletetable(tableName)
        
            
        if match not in [matchlist for matchlist in self.db.select(basedata.matchid, fromtable=basedata.matchlist)]:
            self.db.create_matchTable(title=tableName)
            update_matchtable(match,tableName)

    return matches

def deletetable(self, tableName):
    self.db.run("DROP TABLE "+tableName)

def _parse_matchid(match):
    m = match.split('-')
    m = "_".join(m)
    return m

