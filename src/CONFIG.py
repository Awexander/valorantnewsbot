ANNOUNCECHANNEL = int(1010443668659908788)
LOGCHANNEL      = int(1007170918549819412)
REPORTCHANNEL   = int(1010808789680803871)
RANKCHANNEL     = int(1011240037100310668)
REPORTCARDCHANNEL = int(1015864880722620456)

RED     = 0xF50101
GREEN   = 0x01F501
BLUE    = 0x02AEFD

BOT_TOKEN = ''
SLASH = "/"

NOMATCHPLAYED = {
  "status": 201,
  "errors": [
    {
      "message": "not played any competitive match yet",
      "code": 0,
      "details": "cannot get competitive match data from api call or api did not have any match data for this account"
    }
  ]
}

SUCCESMATCH = {
  "status": 200,
  "errors": [
    {
      "message": "successfully parse match data from api call ",
      "code": 0,
      "details": ""
    }
  ]
}