import os
import json
import asyncio
import datetime as dt
path = os.getcwd()

async def main():
    maintenanceData, incidentData = await getData()
    #print(maintenanceData)
    currMaintenance = await _getstatusData(maintenanceData)
    currIncident = await _getstatusData(incidentData)
    print(currIncident)
    print(currMaintenance)

async def getData():
    with open(f"data/test/update.json", 'r') as w:
        data = json.loads(w.read())
        if bool(data['data']['maintenances']) or bool(data['data']['incidents']):
            return data['data']['maintenances'], data['data']['incidents']
        else: 
            return None, None

async def _getstatusData(data):
    for locale in data[0]['titles']:
        if locale['locale'] == 'en_US':
            title = locale['content']
            break
    
    for translation in data[0]['updates'][0]['translations']:
        if translation['locale'] == 'en_US':
            content = translation['content']
            break
    content_id = data[0]['updates'][0]['id']
    strtime = data[0]['created_at']
    time = dt.datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f%z") + dt.timedelta(hours=8)

    report = {
        'severity': data[0]['incident_severity'],
        'title': title,
        'id': data[0]['id'],
        'content': content,
        'content_id': content_id,
        'time': time.strftime("%B %d, %Y at %H:%M GMT+8"),
        'status': data[0]['maintenance_status']
        }
    return report

asyncio.get_event_loop().run_until_complete(main())