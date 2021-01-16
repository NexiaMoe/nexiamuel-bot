import json
import requests
from script.auth import *
import re

def get_ilust(code, token):
    url = "https://app-api.pixiv.net/v1/illust/detail?illust_id="+str(code)

    payload={}
    headers = {
    'Accept-Language': 'English',
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
    caption = json_data['illust']['caption'].replace("<br />", "\n")
    caption = re.sub(r'<(a|/a).*?>' , "", caption)
    tag = []
    for tags in json_data['illust']['tags']:
        #print(tags)
        #print(tags['name'])
        if tags['translated_name'] is None:
            tag.append(tags['name'])
        else:
            tag.append(tags['translated_name'])
    
    data['data'] = {"id": json_data['illust']['id'],
                    "title": json_data['illust']['title'],
                    "user": json_data['illust']['user']['name'],
                    "user_img": json_data['illust']['user']['profile_image_urls']['medium'],
                    "user_id": json_data['illust']['user']['id'],
                    "caption": caption,
                    "type": json_data['illust']['type'],
                    "page": json_data['illust']['page_count'],
                    "tag": tag,
                    "image": json_data['illust']['meta_single_page']['original_image_url']}
    
    return data

