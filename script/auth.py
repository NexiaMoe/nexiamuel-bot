from datetime import datetime, timezone
import hashlib
import json
import requests

def get_token(username, password):
    client_time = (
            datetime.utcnow()
            .replace(microsecond=0)
            .replace(tzinfo=timezone.utc)
            .isoformat()
        )
    LOGIN_SECRET = ('28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c')

    url = "https://oauth.secure.pixiv.net/auth/token"

    payload={'client_id': 'KzEZED7aC0vird8jWyHM38mXjNTY',
    'client_secret': 'W9JZoJe00qPvJsiyCGT3CCtC6ZUtdpKpzMbNlUGP',
    'get_secure_url': '1',
    'grant_type': 'password',
    'username': username,
    'password': password}
    
    headers = {
    'Accept-Language': 'English',
    # 'X-Client-Time': '2021-01-14T17:15:57+00:00',
    # 'X-Client-Hash': '3fb5de40d13fb037e400dc23781ba779',
    'X-Client-Time': client_time,
    'X-Client-Hash': hashlib.md5((client_time + LOGIN_SECRET).encode('utf-8')).hexdigest(),
    }

    data = {}
    
    
    response = requests.request("POST", url, headers=headers, data=payload).json()
    print(response)
    data['data'] = {'name': response['response']['user']['account'], 'access_token': response['response']['access_token'], 'refresh_token': response['response']['refresh_token']}
    
    with open('option/user.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    return json.dumps(data)