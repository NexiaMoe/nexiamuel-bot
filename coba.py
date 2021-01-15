# string = "https://www.pixiv.net/en/artworks/84752013"
# code = int(''.join(filter(str.isdigit, string))) 

# print(code)

import json

aaa = json.dumps({"data":{"satu": "duar", "dua": "Asu"}})
bbb = json.loads(aaa)

print(bbb['data']['satu'])