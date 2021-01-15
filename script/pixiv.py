import json
import requests
from script.auth import *

def get_ilust(code, token):
    url = "https://app-api.pixiv.net/v1/illust/detail?illust_id="+str(code)

    payload={}
    headers = {
    'Authorization': 'Bearer '+token
    }
    
    # print(token)
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        json_data = response.json()
    elif response.status_code == 404:
        data = "Not Found"
    elif response.status_code == 400:
        with open('option/option.json') as user_token:
            token_data = json.load(user_token)
            tokens = get_token(token_data['username'], token_data['password'])
            
        json_token = json.loads(tokens)
        headers = {
        'Authorization': 'Bearer '+json_token['data']['access_token']
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_data = response.json()
    
    data = {}
    data['data'] = {"id": json_data['illust']['id'],
                    "title": json_data['illust']['title'],
                    "user": json_data['illust']['user']['name'],
                    "image": json_data['illust']['image_urls']['large']}
    
    
    return data

