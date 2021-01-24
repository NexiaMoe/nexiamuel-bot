# -*- coding: utf-8 -*-
import json
import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import asyncio
import aiohttp
import discord
import random
import sqlite3

db = sqlite3.connect('option/site_crawl.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()
db_name = "nhentai"
cursor.execute("CREATE TABLE IF NOT EXISTS 'nhentai' (id INTEGER NOT NULL,title	TEXT,jp	TEXT,cover	TEXT,page	INTEGER,tags	TEXT,chara	TEXT,parody	TEXT,artist	TEXT,languages	TEXT,category	TEXT,groups	TEXT,uploaded	TEXT,PRIMARY KEY(id))")


async def new_upload_code():
    print("Getting New Upload, started at ", datetime.now())
    async with aiohttp.ClientSession() as session:
        async with session.get("https://nhentai.net") as r:
        # r = req.get("https://nhentai.net").text
            if r.status == 429:
                print("Error")
                return
            text = await r.read()
            raw = bs(text, 'html.parser')

            data = raw.find('div', class_="container index-container")
            list_code = []
            for code in data.find_all('a', class_="cover", href=True):
                list_code.append(int(''.join(filter(str.isdigit, code['href']))))
            
            await new_upload(list_code)

async def new_upload(code):
    
    now = datetime.now()
    query = "SELECT id FROM nhentai ORDER BY id DESC LIMIT 1"
    r = cursor.execute(query).fetchone()
     
    data = []
    x = 1
    for i in code:
        print(i)
        # print(i)
        try:
            if r['id'] == i:
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
                    # print(e)
                    time="None"
                try:
                    cover = raw.find("div", {"id": "cover"}).find("img", class_="lazyload")['data-src'] 
                except:
                    cover = ""       
                # Send Message
                x += 1
                cursor.execute("INSERT INTO main." + db_name + " (id, title, jp, cover, page, tags, chara, parody, artist, languages, category, groups, uploaded) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(i, str(title_eng), str(title_jp), str(cover), pages[0], ', '.join(str(x) for x in tag), ', '.join(str(x) for x in chara), ', '.join(str(x) for x in parody), ', '.join(str(x) for x in artist), ', '.join(str(x) for x in language), ', '.join(str(x) for x in category), ', '.join(str(x) for x in groups), str(time)))
                
                db.commit() 
    print("done")

def get_new():
    query = f"SELECT * FROM nhentai ORDER BY id DESC LIMIT 25"
    c = cursor.execute(query)
    r = c.fetchall()
    dujin = []
    
    for data in r:
        dujin.append({'id': data['id'], 'title': data['title'], 'jp': data['jp'], 'cover': data['cover'], 'page': data['page'], 'tags': data['tags'], 'chara': data['chara'], 'parody': data['parody'], 'artist': data['artist'], 'languages': data['languages'], 'category': data['category'], 'groups': data['groups'], 'uploaded': data['uploaded']})
    return dujin

def embed_new(data, i):
        temp = json.loads(json.dumps(data))
        cont = temp[i]
        embed=discord.Embed(title=cont['title'], url="https://nhentai.net/g/"+str(cont['id']), description=cont['jp'], color=0xff0000)
        embed.set_image(url=cont['cover'])
        kode = cont['id']
        embed.add_field(name="Id / Code", value=cont['id'], inline=True)# ', '.join(str(x) for x in parody)
        if cont['parody']:
            embed.add_field(name="Parody", value=cont['parody'].replace(",","\n"), inline=True)
        if cont['artist']:
            embed.add_field(name="Artist", value=cont['artist'].replace(",","\n"), inline=True)
        if cont['groups']:
            embed.add_field(name="Groups", value=cont['groups'].replace(",","\n"), inline=True)
        if cont['chara']:
            embed.add_field(name="Character", value=cont['chara'].replace(",","\n"), inline=True)
        if cont['tags']:
            embed.add_field(name="Tag", value=cont['tags'].replace(",","\n"), inline=True)
        if cont['category']:
            embed.add_field(name="Category", value=cont['category'].replace(",","\n"), inline=True)
        if cont['page']:
            embed.add_field(name="Pages", value=cont['page'], inline=True)
        if cont['languages']:
            embed.add_field(name="Languages", value=cont['languages'].replace(",","\n"), inline=True)
        if cont['uploaded']:
            embed.add_field(name="Uplaoded at", value=cont['uploaded'], inline=True)
        
        # await ctx.send("Requested by {}".format(ctx.message.author.mention))
        # await ctx.send(embed=embed)
        embed.set_footer(text="Doujinshi {} of {}.".format(str(i+1), 25))

        return embed

def random_id():
    query = "SELECT id FROM nhentai ORDER BY id DESC LIMIT 1"
    r = cursor.execute(query).fetchone()
    
    latest = r['id']
    randomize = random.randrange(1, latest)
    # print(randomize)
    return randomize

def get_code(kode):
    r = req.get("https://nhentai.net/g/"+str(kode))
    if r.status_code == 429:
        # embed=discord.Embed(title="nHentai server is busy, Please try again!", color=0xff0000)
        return get_code(kode)
    
    raw = bs(r.text, 'html.parser')
    if r.status_code == 404:
        embed=discord.Embed(title="Code not found!", description="Check code again, or use different code", color=0xff0000)
        return embed
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
        # print(e)
        time="None"
    
    try:
        cover = raw.find("div", {"id": "cover"}).find("img", class_="lazyload")['data-src'] 
    except:
        cover = ""       
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

def tag_search(tag, offset):
    # print(offset)
    all_data = f"SELECT * FROM nhentai WHERE ((tags || languages) LIKE '%{tag}%' OR (languages || tags) LIKE '%{tag}%')"
    query = f"SELECT * FROM nhentai WHERE ((tags || languages) LIKE '%{tag}%' OR (languages || tags) LIKE '%{tag}%') ORDER BY id DESC LIMIT 25 OFFSET {offset}"
    total = len(cursor.execute(all_data).fetchall())
    c = cursor.execute(query)
    r = c.fetchall()
    dujin = []
    
    for data in r:
        dujin.append({'id': data['id'], 'title': data['title'], 'jp': data['jp'], 'cover': data['cover'], 'page': data['page'], 'tags': data['tags'], 'chara': data['chara'], 'parody': data['parody'], 'artist': data['artist'], 'languages': data['languages'], 'category': data['category'], 'groups': data['groups'], 'uploaded': data['uploaded']})
    # print(dujin)
    return total, dujin

def embed_tag(data, i, page_tag, total):
    temp = json.loads(json.dumps(data))
    # print(data)
    # print(i)
    cont = temp[i]
    embed=discord.Embed(title=cont['title'], url="https://nhentai.net/g/"+str(cont['id']), description=cont['jp'], color=0xff0000)
    embed.set_image(url=cont['cover'])
    kode = cont['id']
    embed.add_field(name="Id / Code", value=cont['id'], inline=True)# ', '.join(str(x) for x in parody)
    if cont['parody']:
        embed.add_field(name="Parody", value=cont['parody'].replace(",","\n"), inline=True)
    if cont['artist']:
        embed.add_field(name="Artist", value=cont['artist'].replace(",","\n"), inline=True)
    if cont['groups']:
        embed.add_field(name="Groups", value=cont['groups'].replace(",","\n"), inline=True)
    if cont['chara']:
        embed.add_field(name="Character", value=cont['chara'].replace(",","\n"), inline=True)
    if cont['tags']:
        embed.add_field(name="Tag", value=cont['tags'].replace(",","\n"), inline=True)
    if cont['category']:
        embed.add_field(name="Category", value=cont['category'].replace(",","\n"), inline=True)
    if cont['page']:
        embed.add_field(name="Pages", value=cont['page'], inline=True)
    if cont['languages']:
        embed.add_field(name="Languages", value=cont['languages'].replace(",","\n"), inline=True)
    if cont['uploaded']:
        embed.add_field(name="Uplaoded at", value=cont['uploaded'], inline=True)
    
    # await ctx.send("Requested by {}".format(ctx.message.author.mention))
    # await ctx.send(embed=embed)
    embed.set_footer(text="Total Doujin : {}, Doujinshi {} of {}.\nPages {} of {}.".format(total, str(i+1), 25, page_tag, total//25))

    return embed

def artist_search(artist, offset):
    all_data = f"SELECT * FROM nhentai WHERE artist LIKE '%{artist}%'"
    query = f"SELECT * FROM nhentai WHERE artist LIKE '%{artist}%' ORDER BY id DESC LIMIT 25 OFFSET {offset}"
    total = len(cursor.execute(all_data).fetchall())
    c = cursor.execute(query)
    r = c.fetchall()
    dujin = []
    
    for data in r:
        dujin.append({'id': data['id'], 'title': data['title'], 'jp': data['jp'], 'cover': data['cover'], 'page': data['page'], 'tags': data['tags'], 'chara': data['chara'], 'parody': data['parody'], 'artist': data['artist'], 'languages': data['languages'], 'category': data['category'], 'groups': data['groups'], 'uploaded': data['uploaded']})
    return total, dujin

def embed_artist(data, i, page_tag, total):
    temp = json.loads(json.dumps(data))
    cont = temp[i]
    embed=discord.Embed(title=cont['title'], url="https://nhentai.net/g/"+str(cont['id']), description=cont['jp'], color=0xff0000)
    embed.set_image(url=cont['cover'])
    kode = cont['id']
    embed.add_field(name="Id / Code", value=cont['id'], inline=True)# ', '.join(str(x) for x in parody)
    if cont['parody']:
        embed.add_field(name="Parody", value=cont['parody'].replace(",","\n"), inline=True)
    if cont['artist']:
        embed.add_field(name="Artist", value=cont['artist'].replace(",","\n"), inline=True)
    if cont['groups']:
        embed.add_field(name="Groups", value=cont['groups'].replace(",","\n"), inline=True)
    if cont['chara']:
        embed.add_field(name="Character", value=cont['chara'].replace(",","\n"), inline=True)
    if cont['tags']:
        embed.add_field(name="Tag", value=cont['tags'].replace(",","\n"), inline=True)
    if cont['category']:
        embed.add_field(name="Category", value=cont['category'].replace(",","\n"), inline=True)
    if cont['page']:
        embed.add_field(name="Pages", value=cont['page'], inline=True)
    if cont['languages']:
        embed.add_field(name="Languages", value=cont['languages'].replace(",","\n"), inline=True)
    if cont['uploaded']:
        embed.add_field(name="Uplaoded at", value=cont['uploaded'], inline=True)
    
    # await ctx.send("Requested by {}".format(ctx.message.author.mention))
    # await ctx.send(embed=embed)
    embed.set_footer(text="Total Doujin : {}, Doujinshi {} of {}.\nPages {} of {}.".format(total, str(i+1), 25, page_tag, total//25))

    return embed