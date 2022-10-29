
from .mysql import mysql
from .config import basedata

class database:
    def __init__(self):
        self.db = mysql()

    def update_matchtable(self, matchreport, tableName):
        #get players column
        
        matchid = matchreport.get('matchid')
        mapName = matchreport.get('map')
        time = matchreport.get('timeplayed')
        mode = matchreport.get('gamemode')
        red = matchreport.get('result').get('red')
        blue = matchreport.get('result').get('blue')
        players = matchreport.get('players')

        #update matchlist first before update individual match
        self.db.insert(  
            fromtable=basedata.matchlist, 
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
            self.db.insert(
                fromtable=tableName,
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

    def savematch(self, matchdetails):
        matchid = matchdetails.get('matchid')
        tableName = "match_" + self._parse_matchid(matchid)
        
        matcheslist = self.db.select(basedata.matchid, fromtable=basedata.matchlist)
        if matcheslist is False: return False

        #print(match not in [matchlist[0] for matchlist in matcheslist])
        if matchid not in [matchlist[0] for matchlist in matcheslist]:
            if tableName in self.db.tables():
                self.db.run(f"DELETE FROM {basedata.matchlist} WHERE matchid='{matchid}';")
                self.deletetable(tableName)
            self.db.create_matchTable(title=tableName)
            self.update_matchtable(matchdetails, tableName)

        return matchid

    def deletetable(self, tableName):
        self.db.run("DROP TABLE "+tableName)

    def _parse_matchid(self, match):
        m = match.split('-')
        m = "_".join(m)
        return m
