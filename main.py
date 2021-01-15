# from pixivapi import Client

# client = Client()

# # client.login('nexiamuel', '3Dogawac0nan')
# # refresh_token = client.refresh_token
# client.authenticate('bswCySoet3ntspHCtVQCMYVHygCkat5m-f_y8LkDjCo')

# test = client.fetch_illustration(59580629).
# print(test)

# import requests
# import json


# test = '87054348'
# headers = {
#   'accept': 'application/json',
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
#   'x-user-id': '22668987',
#   'Sec-Fetch-Site': 'same-origin',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Dest': 'empty',
#   'Cookie': '__cfduid=d41d3e6dfabad96fb0af0947c539487941610641614; PHPSESSID=gsctbvbm93gnlt7mrr4107v3egdonioi; yuid_b=Eidgh3U; __cf_bm=db72f5d08a7e246a4a0f194e9539187c5aa0536f-1610642520-1800-AdtonhFbrcEXK7+aGnwZw4UcSbVB8cet1LcdXRPJHs0y9fR9+MqCAAyLqzFx9ETu+hepWnzLiMCsJ0Lz5Q4fOE8='
# }
# head2 = {
#     'Referer': 'https://pixiv.net'
# }
# ilust = requests.get("https://www.pixiv.net/ajax/illust/"+test+"?lang=en", headers=headers).text
# ilust2 = requests.get("https://i.pximg.net/img-master/img/2021/01/15/00/30/11/87054348_p0_master1200.jpg", headers=head2).text

# hasil = json.loads(ilust)

# print(type(hasil))
# print(ilust2)

from auth import get_token

get_token('nexiamuel', '3Dogawac0nan')