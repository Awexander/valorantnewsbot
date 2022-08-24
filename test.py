import asyncio
import json
from src.test import api
from src.test import open

asyncio.get_event_loop().run_until_complete(api.main())