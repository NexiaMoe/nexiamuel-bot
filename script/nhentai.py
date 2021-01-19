# -*- coding: utf-8 -*-
import json
import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import asyncio
import aiohttp
import discord
import random

async def new_upload_code():
    print("Getting New Upload, started at ", datetime.now())
    async with aiohttp.ClientSession() as session:
        async with session.get("https://nhentai.net") as r:
        # r = req.get("https://nhentai.net").text
            text = await r.read()
            raw = bs(text, 'html.parser')

            data = raw.find('div', class_="container index-container")
            list_code = []
            for code in data.find_all('a', class_="cover", href=True):
                list_code.append(int(''.join(filter(str.isdigit, code['href']))))
            
            await new_upload(list_code)

async def new_upload(code):
    now = datetime.now()
    try:
        with open("option/nhentai_new.json", "r", encoding='utf-8')as f:
            temp = json.load(f)
    except json.decoder.JSONDecodeError:
        pass
    
    data = []
    x = 1
    for i in code:
        # print(i)
        try:
            if temp[0]['id'] == i:
                print("Newest manga is detected, stopping")
                print(f"Done at {now}")
                break
        except Exception:
            pass
        # if x < 3:
        # print("Crawling", x, "Of", len(code))
        async with aiohttp.ClientSession() as session:
            async with session.get("https://nhentai.net/g/"+str(i)) as r:
            # r = req.get("https://nhentai.net/g/"+str(i)).text
                text = await r.read()
                raw = bs(text, 'html.parser')
                try:
                    title_eng = raw.find("h1", class_="title").text
                except AttributeError:
                    title_eng = ""
                try:
                    title_jp = raw.find("h2", class_="title").text
                except AttributeError:
                    title_jp = ""
                    
                tag = []
                chara = []
                parody = []
                artist = []
                language = []
                category = []
                pages = []
                groups = []
                
                try:
                    for p in raw.find_all("span", class_="tags")[0].find_all("span", class_="name"):
                        parody.append(p.text.capitalize())
                except:
                    parody.append("")

                try:
                    for charachter in raw.find_all("span", class_="tags")[1].find_all("span", class_="name"):
                        chara.append(charachter.text.capitalize())
                except:
                    chara.append("")

                try:
                    for tag_all in raw.find_all("span", class_="tags")[2].find_all("span", class_="name"):
                        tag.append(tag_all.text.capitalize())
                except:
                    tag.append("")

                try:
                    for ar in raw.find_all("span", class_="tags")[3].find_all("span", class_="name"):
                        artist.append(ar.text.capitalize())
                except:
                    artist.append("")
                    
                try:
                    for gr in raw.find_all("span", class_="tags")[4].find_all("span", class_="name"):
                        groups.append(gr.text.capitalize())
                except:
                        groups.append("")

                try:
                    for la in raw.find_all("span", class_="tags")[5].find_all("span", class_="name"):
                        language.append(la.text.capitalize())
                except:
                    language.append("")
                        
                try:
                    for ca in raw.find_all("span", class_="tags")[6].find_all("span", class_="name"):
                        category.append(ca.text.capitalize())
                except:
                        category.append("")
                        
                try:
                    for pg in raw.find_all("span", class_="tags")[7].find_all("span", class_="name"):
                        pages.append(pg.text.capitalize())
                except:
                    pages.append("")
                    
                try:     
                    for up in raw.find_all("span", class_="tags")[8]:
                        clock = str(up['datetime']).replace("T", " ").replace("+00:00", "")
                        time = datetime.strptime(clock, '%Y-%m-%d %H:%M:%S.%f')
                except Exception as e:
                    print(e)
                    time="None"
                
                cover = raw.find("div", {"id": "cover"}).find("img", class_="lazyload")['data-src']        
                # Send Message
                data.append({'id': i, 'eng': title_eng, 'jp': title_jp, 'cover': cover, 'page': pages[0], 'tags': tag, 'chara': chara, 'parody': parody, 'artist': artist, 'languages': language, 'category': category, 'groups': groups, 'uploaded': str(time)})
                
                x += 1
                # else:
                #     break
    if data is []:
        return
    else:
        try:
            for a in temp:
                    data.append(a)
        except :
            pass
    with open('option/nhentai_new.json', 'w', encoding='utf8') as f:
        # json.dumps(data, ensure_ascii=False, indent=4)
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("done")

def pages(pages):
    with open("option/nhentai_new.json", 'r', encoding='utf-8') as f:
        temp = json.load(f)
    cont = temp[pages]
    embed=discord.Embed(title=cont['eng'], url="https://nhentai.net/g/"+str(cont['id']), description=cont['jp'], color=0xff0000)
    embed.set_image(url=cont['cover'])
    kode = cont['id']
    embed.add_field(name="Id / Code", value=', '.join(str(x) for x in cont['kode']), inline=True)# ', '.join(str(x) for x in parody)
    if cont['parody']:
        embed.add_field(name="Parody", value=', '.join(str(x) for x in cont['parody']), inline=True)
    if cont['artist']:
        embed.add_field(name="Artist", value=', '.join(str(x) for x in cont['artist']), inline=True)
    if cont['groups']:
        embed.add_field(name="Groups", value=', '.join(str(x) for x in cont['groups']), inline=True)
    if cont['chara']:
        embed.add_field(name="Character", value=', '.join(str(x) for x in cont['chara']), inline=True)
    if cont['tags']:
        embed.add_field(name="Tag", value=f'\n'.join(str(x) for x in cont['tags']), inline=True)
    if cont['category']:
        embed.add_field(name="Category", value=', '.join(str(x) for x in cont['category']), inline=True)
    if cont['page']:
        embed.add_field(name="Pages", value=cont['page'], inline=True)
    if cont['languages']:
        embed.add_field(name="Languages", value=', '.join(str(x) for x in cont['languages']), inline=True)
    if cont['uploaded']:
        embed.add_field(name="Uplaoded at", value=cont['uploaded'], inline=True)
    
    # await ctx.send("Requested by {}".format(ctx.message.author.mention))
    # await ctx.send(embed=embed)
    embed.set_footer(text="Doujinshi {} of {}. Use emojis below to select new doujinshi released.".format(str(pages+1), str(len(temp))))

    return embed

def random_id():
    with open("option/nhentai_new.json", "r", encoding='utf-8') as f:
       temp =  json.load(f)
    
    latest = temp[0]['id']
    randomize = random.randrange(1, latest)
    # print(randomize)
    return randomize

def get_code(kode):
    r = req.get("https://nhentai.net/g/"+str(kode)).text
    raw = bs(r, 'html.parser')
    try:
        title_eng = raw.find("h1", class_="title").text
    except AttributeError:
        title_eng = ""
    try:
        title_jp = raw.find("h2", class_="title").text
    except AttributeError:
        title_jp = ""
        
    tag = []
    chara = []
    parody = []
    artist = []
    language = []
    category = []
    pages = []
    groups = []
    
    try:
        for p in raw.find_all("span", class_="tags")[0].find_all("span", class_="name"):
            parody.append(p.text.capitalize())
    except:
        parody.append("")

    try:
        for charachter in raw.find_all("span", class_="tags")[1].find_all("span", class_="name"):
            chara.append(charachter.text.capitalize())
    except:
        chara.append("")

    try:
        for tag_all in raw.find_all("span", class_="tags")[2].find_all("span", class_="name"):
            tag.append(tag_all.text.capitalize())
    except:
        tag.append("")

    try:
        for ar in raw.find_all("span", class_="tags")[3].find_all("span", class_="name"):
            artist.append(ar.text.capitalize())
    except:
        artist.append("")
        
    try:
        for gr in raw.find_all("span", class_="tags")[4].find_all("span", class_="name"):
            groups.append(gr.text.capitalize())
    except:
            groups.append("")

    try:
        for la in raw.find_all("span", class_="tags")[5].find_all("span", class_="name"):
            language.append(la.text.capitalize())
    except:
        language.append("")
            
    try:
        for ca in raw.find_all("span", class_="tags")[6].find_all("span", class_="name"):
            category.append(ca.text.capitalize())
    except:
            category.append("")
            
    try:
        for pg in raw.find_all("span", class_="tags")[7].find_all("span", class_="name"):
            pages.append(pg.text.capitalize())
    except:
        pages.append("")
        
    try:     
        for up in raw.find_all("span", class_="tags")[8]:
            clock = str(up['datetime']).replace("T", " ").replace("+00:00", "")
            time = datetime.strptime(clock, '%Y-%m-%d %H:%M:%S.%f')
    except Exception as e:
        print(e)
        time="None"
    
    cover = raw.find("div", {"id": "cover"}).find("img", class_="lazyload")['data-src']        
    # Send Message
    embed=discord.Embed(title=title_eng, url="https://nhentai.net/g/"+str(kode), description=title_jp, color=0xff0000)
    embed.set_image(url=cover)
    # ', '.join(str(x) for x in parody)
    embed.add_field(name="ID / Code", value=kode, inline=True)
    if parody:
        embed.add_field(name="Parody", value=', '.join(str(x) for x in parody), inline=True)
    if artist:
        embed.add_field(name="Artist", value=', '.join(str(x) for x in artist), inline=True)
    if groups:
        embed.add_field(name="Groups", value=', '.join(str(x) for x in groups), inline=True)
    if chara:
        embed.add_field(name="Character", value=', '.join(str(x) for x in chara), inline=True)
    if tag:
        embed.add_field(name="Tag", value=f'\n'.join(str(x) for x in tag), inline=True)
    if category:
        embed.add_field(name="Category", value=', '.join(str(x) for x in category), inline=True)
    if pages:
        embed.add_field(name="Pages", value=', '.join(str(x) for x in pages), inline=True)
    if language:
        embed.add_field(name="Languages", value=', '.join(str(x) for x in language), inline=True)
    if timedelta:
        embed.add_field(name="Uplaoded at", value=time, inline=True)
    
    return embed