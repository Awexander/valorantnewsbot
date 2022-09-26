
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont   
import json

class reportcard():
    def __init__(self) -> None:
        self.fontStat = ImageFont.truetype('assets/fonts/LinkStart.ttf', 36)
        self.fontName = ImageFont.truetype('assets/fonts/DINNextLTPro-Bold.ttf', 20)
        self.fontMVPStat = ImageFont.truetype('assets/fonts/LinkStart.ttf', 100)
        self.fontMVPName = ImageFont.truetype('assets/fonts/DINNextLTPro-Bold.ttf', 50)
        self.fontMap = ImageFont.truetype('assets/fonts/LinkStart.ttf', 120)
        self.fontScore = ImageFont.truetype('assets/fonts/LinkStart.ttf', 150)
        pass

    async def card(self, match):
        mvpRedValue, mvpBlueValue = 0,0
        players = {}
        for player in match['players']:
            if player['team'].lower() == 'red':
                if player['acs'] > mvpRedValue:
                    mvpRedValue = player['acs']
                    mvpRed = player
            if player['team'].lower() == 'blue':
                if player['acs'] > mvpBlueValue:
                    mvpBlueValue = player['acs']
                    mvpBlue = player

            image = await self._drawAgents(player)
            players.update({
                f"{player['name']}": 
                {
                    "mvp": False,
                    "team": player['team'],
                    "image":image
                }})
        
        imageRed = await self._drawMVP(mvpRed)
        imageBlue = await self._drawMVP(mvpBlue)
        players.update({f"{mvpRed['name']}": 
                {
                    "mvp": True,
                    "team": mvpRed['team'],
                    "image":imageRed
                }, 
                f"{mvpBlue['name']}":
                {
                    "mvp": True,
                    "team": mvpBlue['team'],
                    "image":imageBlue
                }})
        img = {
            "map": match.get('map'),
            "result": match.get('result'),
            "timeplayed": match.get('timeplayed'),
            "player": players
        }
         
        report = await self._drawReport(img)
        report.save(f"data/match/reportcard/{match.get('matchid')}.png")
        #return report
        return match.get('matchid')

    async def _drawReport(self, img):
        background = Image.open('assets/background.png')
        coordRed = [(30, 775), (260, 775), (490, 775), (720, 775)]
        coordBlue = [(975, 775), (1205, 775), (1435, 775), (1665, 775)]
        aRed, aBlue = 0,0
        for i in img.get('player').values():
            if i.get('mvp') == True:
                card = i.get('image')
                if i.get('team').lower() == 'red':
                    background.paste(card, (30, 208), card)
                else:
                    background.paste(card, (975, 208), card)
            else:
                card = i.get('image')
                if i.get('team').lower() == 'red':
                    background.paste(card, coordRed[aRed], card)
                    aRed += 1
                else:
                    background.paste(card, coordBlue[aBlue], card)
                    aBlue += 1
        
        map = await self._drawMap(img)
        background.paste(map, (30, 25), map)

        scoreRed = ImageDraw.Draw(background)
        xRed, yRed = self._scoreRedCenter(img.get('result').get('red'))
        xBlue, yBlue = self._scoreRedCenter(img.get('result').get('blue'))
        scoreRed.text((975+xRed, 20+yRed), text=str(img.get('result').get('red')), font=self.fontScore)
        scoreRed.text((1445+xBlue, 20+yBlue), text=str(img.get('result').get('blue')), font=self.fontScore)

        return background

    async def _drawAgents(self, player):
        rankImage = await self._rank(player['rank'])
        agentImage = await self._agents(player['agent'])

        drawing = ImageDraw.Draw(agentImage)
        drawing.text((170+self._fontStatCenter(player['adr']), 75), text=str(player['adr']), font=self.fontStat)
        drawing.text((170+self._fontStatCenter(player['kda'][3]), 125), text=str(player['kda'][3]), font=self.fontStat)
        drawing.text((170+self._fontStatCenter(player['headshot']), 175), text=str(player['headshot']), font=self.fontStat)
        drawing.text((3, 268), f"{player['name']}#{player['tag']}", font=self.fontName)

        agentImage.paste(rankImage, (165, 5), rankImage)
        #agentImage.save(f"data/match/reportcard/{player['name']}#{player['tag']}.png")
        return agentImage

    async def _drawMVP(self, player):
        rankImage = await self._rank(player['rank'], mvp=True)
        agentImage = await self._agents(player['agent'], mvp=True)

        drawing = ImageDraw.Draw(agentImage)
        drawing.text((500+self._MVPfontCenter(player['adr']),270), text=str(player['adr']), font=self.fontMVPStat)
        drawing.text((650+self._MVPfontCenter(player['kda'][3]),270), text=str(player['kda'][3]), font=self.fontMVPStat)
        drawing.text((790+self._MVPfontCenter(player['headshot']),270), text=str(player['headshot']), font=self.fontMVPStat)
        drawing.text((400, 500), f"{player['name']}#{player['tag']}", font=self.fontMVPName)

        agentImage.paste(rankImage, (790, 15), rankImage)
        return agentImage
    
    async def _drawMap(self, img):
        map = Image.open(f"assets/maps/{img.get('map')}.png")
        draw = ImageDraw.Draw(map)
        draw.text((15, 15), text=img.get('map').upper(), font=self.fontMap)
        draw.text((15, 110), text=img.get('timeplayed').upper(), font=self.fontName)

        return map

    def _MVPfontCenter(self, text):
        w = self.fontMVPStat.getbbox(str(text))
        width = (75 - (w[2] - w[0])) / 2
        return width

    def _fontStatCenter(self, text):
        w = self.fontStat.getbbox(str(text))
        width = (35 - (w[2] - w[0])) / 2
        return width 
    
    def _scoreRedCenter(self, text):
        w = self.fontScore.getbbox(str(text))
        width = (450 - (w[2] - w[0])) / 2
        height = (170 - (w[3] - w[1])) / 2
        return width , height

    async def _agents(self, id, mvp=False):
        with open('assets/agents.json', 'r') as r:
            agents = json.loads(r.read())
            for agent in agents:
                if agent['agentName'] == id:
                    if mvp == False:
                        path = agent['small']
                    else:
                        path = agent['mvp']

                    return Image.open(path)

    async def _rank(self, rank, mvp=False):
        with open('assets/ranks.json', 'r') as r:
            ranks = json.loads(r.read())
            for r in ranks:
                if r['rank'] == rank:
                    path = r['image']
                    if mvp == False:
                        return Image.open(path).resize((50,50))
                    else:
                        return Image.open(path).resize((100, 100))
    

