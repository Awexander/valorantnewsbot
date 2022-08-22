import aiohttp
import asyncio
import datetime as dt
import json
import getmatches as match

statusURL = 'https://api.henrikdev.xyz/valorant/v1/status/ap'
matchupdate = match.getmatchinfo()

async def main():
    incidentData, error = await matchupdate.getmatches('belangsukawa', '111')
    print(error)

async def _getIncident(incidentData):
    for locale in incidentData[0]['titles']:
        if locale['locale'] == 'en_US':
            incident = locale['content']
            break
    
    for translation in incidentData[0]['updates'][0]['translations']:
        if translation['locale'] == 'en_US':
            content = translation['content']
            break
    strtime = incidentData[0]['created_at']
    time = dt.datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f%z") + dt.timedelta(hours=8)

    report = {'severity': incidentData[0]['incident_severity'].upper(),
        'incident': incident,
        'content': content,
        'time': time.strftime("%B %d, %Y at %H:%M GMT+8")
        }
    return report

async def _requestsupdates(url):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as session:
            async with session.get(statusURL) as response:
                resp = await response.json()

        if url == statusURL:
            data = resp['data']
            return data['maintenances'], data['incidents']

    except Exception as error:
        print(error)

asyncio.get_event_loop().run_until_complete(main())
