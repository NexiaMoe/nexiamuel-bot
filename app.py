from io import BytesIO
import discord
from discord.ext import commands, tasks
from discord.utils import get
import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import re
import os.path
import time
import threading
import asyncio
import sqlite3

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from script.auth import *
from script.pixiv import *
from script.nhentai import *


db = sqlite3.connect('option/server.db')
cursor = db.cursor()
db_name = "settings"
cursor.execute("CREATE TABLE IF NOT EXISTS "+db_name+" (id INTEGER NOT NULL,server_name	TEXT,category_id	INTEGER,category_name	TEXT,prefix TEXT, PRIMARY KEY(id))")


def get_prefix(client, message):
    global prefix
    c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(message.guild.id),))
    data = c.fetchone()
    if data is None:
        cursor.execute("INSERT OR IGNORE INTO "+db_name+" (id, server_name, category_id, category_name, prefix) VALUES(?, ?, ?, ?, ?)", (int(message.guild.id), str(message.guild), int("0"), str(""), str("g/"),))
        return "g/"
    else:
        c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(message.guild.id),))
        prefix = ''.join(c.fetchone())
    # print(prefix)
    # print(prefix)
        return prefix

client = commands.Bot(command_prefix=get_prefix)

client.remove_command("help")
@client.event
async def on_guild_join(guild):
    cursor.execute("INSERT INTO "+db_name+" (id, server_name, category_id, category_name, prefix) VALUES(?, ?, ?, ?, ?)", (int(guild.id), str(guild), int("0"), str(""), str("g/"),))
    db.commit()

@client.command()
@commands.has_permissions(administrator = True)
async def changeprefix(ctx, prefix):
    # print(prefix)
    c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(ctx.guild.id),))
    data = c.fetchone()
    if data == None:
        cursor.execute("INSERT INTO "+db_name+" (id, server_name, category_id, category_name, prefix) VALUES(?, ?, ?, ?, ?)", (int(ctx.guild.id), str(ctx.guild), int("0"), str(""), str(prefix),))
        db.commit()
        await ctx.send(f"Prefix has been set to {prefix}")
    else:
        query = f"UPDATE {db_name} SET prefix = '{prefix}' WHERE id == {ctx.guild.id}"
        cursor.execute(query)
        db.commit()
        await ctx.send(f"Prefix has been set to {prefix}")
# prefix = ""

@client.event 
async def on_command_error(ctx, error):
    # global prefix
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found, please use {prefix}help command to get list of command!")
        return
    raise error

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Nexiamuel NSFW Bot",description=f"""
    This bot is useful to get doujinshi information from nHentai.

    To get start, just send command `code <code>`, and the bot will processed the code and will s>

    Please check the command_prefix, Default is g/
    
    __***Command***__

    **nHentai**
    - `code <code>` : Get information of Doujinshi from nHentai
    - `ping` : Get status from Bot
    - `help` : Open this help
    - `view <code>` : View Doujinshi to secret channel
    - `random` : Get random code / Gacha.
    - `new` : Get latest dujin, updated an hour.
    - `close` : To Close secret channel, must on the right category channel.
   
    **pixiv**
    - `pixiv <code> / <url>` : Get illustrator from pixiv
    
    **Bot Settings**
    - `changeprefix <prefix> or setprefix <prefix>` : Change bot prefix on this server
    - `prefix` : Get prefix on this server
    - `setreadcategory <category>` : Set category channel to read
    Will be add more feature!""" , color=0x00ccff)
    await ctx.send(embed=embed)

@client.event
async def on_ready():
    print("bot is ready")

@client.event
async def on_message(ctx):
    c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(ctx.guild.id),))
    pre  = ''.join(c.fetchone())
    try:
        a = ctx.content
        num = int(a.replace(".",""))
    except:
        num = ctx.content
        await client.process_commands(ctx)
        pass
    try:
        
        if ctx.content.startswith(pre + str(num)):
            print(ctx.content)
            embed = get_code(int(''.join(filter(str.isdigit, ctx.content))))

            await ctx.channel.send("Requested by {}".format(ctx.author.mention))
            await ctx.channel.send(embed=embed)
        
            
    except Exception as e:
        print(e)
        await client.process_commands(ctx)
        
        pass  
    # await client.process_commands(ctx)
    
@tasks.loop(hours=1)
async def sched_new():
    # print("Disabled")
    await new_upload_code()
    
@sched_new.before_loop
async def before_sched():
    print("Waiting bot to start..")
    await client.wait_until_ready()

@client.command()
async def ping(ctx):
    await ctx.send("Pong")

@client.command(pass_context = True)
async def code(ctx, kode : int):
    """To get information of code from nHentai
    
    """
    # Process
    # print("Processing", kode)
    embed = get_code(kode)
    
    await ctx.send("Requested by {}".format(ctx.message.author.mention))
    await ctx.send(embed=embed)
    
    # This is currently not work, so leave this...
    # await ctx.send("Use **g/read 'insert code here'** to Read, or **g/download 'insert code here'** for download as zip")
    # print("Done")

@code.error
async def code_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Wrong code, please use integer only or Check if the code is correct!")
    else:
        print(error)

@client.command()
async def clear(ctx):
    await ctx.channel.purge()

@client.command(pass_context = True)
async def view(ctx, kode : int):
    """Read Doujin from nHentai
    
    """
    print(kode)
    channel = discord.utils.get(ctx.guild.channels, name=str(kode))
    c = cursor.execute("SELECT * FROM "+db_name+" WHERE id == ?", (int(ctx.message.guild.id),))
    try:
        for data in c.fetchall():
            category_id = data[2]
            server_id = data[0]
            category_name = data[3]
    except:
        await ctx.send(f"Please configure category name to read with {prefix}!")
    if channel is None:
        guild = ctx.guild
        if str(ctx.message.guild.id) == str(server_id):
            name = category_name
            category = discord.utils.get(ctx.guild.categories, name=name)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            await guild.create_text_channel(kode, category=category, overwrites=overwrites)
            channel = discord.utils.get(ctx.guild.channels, name=str(kode))
            
            async with aiohttp.ClientSession() as session:
                async with session.get("https://nhentai.net/g/"+str(kode)+"/1") as r:
                #url = req.get("https://nhentai.net/g/"+str(kode)+"/1")
                    text = await r.read()
                    raw = bs(text, 'html.parser')
                    link = []

                    total_pages = int(raw.find("span", class_="num-pages").text) + 1
                    #print(total_pages)
                    total_pages = int(raw.find("span", class_="num-pages").text) + 1
                    # print(total_pages)

                    ext=".jpg"
                    media_id = raw.find("section", {"id": "image-container"}).find("img")['src'].replace("https://i.nhentai.net/galleries/","").replace("/1.jpg","")
                    if re.findall(r"png",media_id):
                        ext = ".png"
                        media_id = raw.find("section", {"id": "image-container"}).find("img")['src'].replace("https://i.nhentai.net/galleries/","").replace("/1.png","")

                    for a in range(1, total_pages):
                        link.append("https://i.nhentai.net/galleries/"+str(media_id)+"/"+str(a)+ext)
                        
                    await channel.send(f"Total Pages : {total_pages}")
                    for kirim in link:
                        await channel.send(kirim)
                    await channel.send("Done, Enjoy!")
                    await channel.send("Jangan lupa hapus channel dengan command .close!")
                        
        
        
    else:
        # print("sudah ada")
        overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await channel.set_permissions(ctx.author, overwrite=overwrite)

@client.command(pass_context = True)
async def setreadcategory(ctx, *, channel):
    channel_name = discord.utils.get(ctx.guild.categories, name=channel)
    query = f"UPDATE {db_name} set category_id = {channel_name.id}, category_name = '{channel_name}' WHERE id = {ctx.message.guild.id}"
    cursor.execute(query)
    db.commit()
    await ctx.send(f"Category **{channel}** has been set to read Doujinshi")
    # try:
    #     try:
    #         with open('option/server.json') as f:
    #             temp = json.load(f)
    #     except :
    #         temp=[]
    #         pass
            
    #     x = 0
    #     channel_name = discord.utils.get(ctx.guild.categories, name=channel)
    #     new_data = []
    #     try:
    #         for entry in temp:
    #             if entry['server_id'] == ctx.message.guild.id:
    #                 s_id = entry['server_id']
    #                 s_name = entry['server_name']
    #                 new_data.append({'server_id': s_id, 'server_name': s_name, 'channel_read_id': channel_name.id, 'channel_read_name': str(channel_name)})
    #                 x+=1
                                
    #             elif entry['server_id'] != ctx.message.guild.id:
    #                 x == 0
    #                 new_data.append(entry)
                    
    #             else: 
    #                 x+=1
    #                 new_data.append(entry)
    #     except:
    #         s_id = ctx.message.guild.id
    #         s_name = ctx.message.guild.name
    #         new_data.append({'server_id': s_id, 'server_name': s_name, 'channel_read_id': channel_name.id, 'channel_read_name': str(channel_name)})
    #     with open('option/server.json', "w") as f:
    #         json.dump(new_data, f, indent=4)  
            
    #     if x == 0:
    #         server = {}
    #         server['server_id'] = ctx.message.guild.id
    #         server['server_name'] = ctx.message.guild.name
    #         server['channel_read_id'] = channel_name.id
    #         server['channel_read_name'] = str(channel_name)
    #         temp.append(server)
    #         with open('option/server.json', "w") as f:
    #             json.dump(temp, f, indent=4)
    #     await ctx.send(f"Category **{channel}** has been set to read Doujinshi")
    # except AttributeError:
    #     await ctx.send("Please check the category name")
    # except Exception:
    #     await ctx.send("The are error ask bot owner mistake or open Issues in github!")
        
@setreadcategory.error
async def setreadcategory_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Command missing arguments, need Category name! Please add category to make bot can make channel on category for view nHentai page!")
        await ctx.send("Use setreadcategory <category name>")
        
    else:
        print(error)

@client.command(pass_context = True)
async def new(ctx):
    b_text = await ctx.send("Get new release...")
    
    kode = 0
    await b_text.delete()
    await ctx.message.delete()
    temp = get_new()
    # pages = [page1, page2, page3]
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    message = await ctx.send(embed = embed_new(temp, 0))
    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')
    await message.add_reaction(cross)
    await message.add_reaction(open_book)
    await message.add_reaction('⭕')

    def check(reaction, user):
        
        return reaction.message.id == reaction.message.id

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = embed_new(temp, i))
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = embed_new(temp, i))
        elif str(reaction) == '▶':
            if i < len(temp)-1:
                i += 1
                await message.edit(embed = embed_new(temp, i))
        elif str(reaction) == '⏭':
            i = len(temp)-1
            await message.edit(embed = embed_new(temp, i))
        elif str(reaction) == cross:
            await message.delete()
        elif str(reaction) == open_book:
            await view(ctx, json.loads(json.dumps(temp))[i]['id'])
            await message.edit(content="Opened.")
            
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 300.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()
    await message.delete()

@client.command(pass_context = True) 
async def close(ctx):
    """Close Doujinshi channel
    
    """
    with open("option/server.json", 'r') as f:
        temp = json.load(f)
    for code in temp:
        if str(ctx.message.guild.id) == str(code['server_id']):
            name = code['channel_read_name']
            category = discord.utils.get(ctx.guild.categories, name=name)
            #print(category.id)
            if ctx.message.channel.category.id is not category.id:
                await ctx.send("Salah channel Cok!")
                #print(ctx.message.channel.category.id)
            else:
                channel = ctx.message.channel
                channel = discord.utils.get(ctx.guild.channels, name=str(channel))
                await channel.delete()
                break

@client.command(pass_context = True)
async def random(ctx):
    randomize = random_id()
    embed = get_code(randomize)
    await ctx.send("Hey {}, You get this:".format(ctx.message.author.mention))
    await ctx.send(embed=embed)
    
@client.command(pass_context = True)
async def tag(ctx, tags):
    await ctx.message.delete()
    start = 0
    end = 25
    total, temp = tag_search(tags, start, end)
    page_tag = 1
    # print(temp)
    
    
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    message = await ctx.send(embed = embed_tag(temp, 0, page_tag, total))
    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')
    await message.add_reaction(cross)
    await message.add_reaction(open_book)
    await message.add_reaction('⭕')

    def check(reaction, user):
        
        return reaction.message.id == reaction.message.id
    i = 0
    reaction = None
    while True:
        if str(reaction) == '⏮':
            
            if start > 0:
                start = start - 25
            if end >= 25:
                end = end - 25
            i = 0
            
            if page_tag > 1:
                page_tag = page_tag - 1
                total, temp = tag_search(tags, start, end)
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '◀':
            if i > 0:
                i = i - 1
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '▶':
            if i < 25:
                i = i + 1
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '⏭':
            start = start + 25
            end = end + 25
            i = 0
            page_tag = page_tag + 1
            total, temp = tag_search(tags, start, end)
            await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == cross:
            await message.delete()
        elif str(reaction) == open_book:
            await view(ctx, json.loads(json.dumps(temp))[i]['id'])
            await message.edit(content="Opened.")
            
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 300.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    await message.clear_reactions()
    await message.delete() 


# Pixiv Command :

@client.command(pass_context = True) 
async def pixiv(ctx, *, data):
    await ctx.send("Processing, Please wait...")
    try:
        int(data)
        data = int(data)
    except ValueError:
        data = int(''.join(filter(str.isdigit, data))) 
        pass
    
    if os.path.isfile('option/user.json'):
        with open('option/user.json') as json_file:
            json_data = json.load(json_file)
            ilust = get_ilust(data, json_data['data']['access_token'])
            headers = {
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Dest': 'document',
                        'Referer': 'https://pixiv.net'
                    }   
            
            with BytesIO(req.get(ilust['data']['image'], headers=headers).content) as image_binary:
                image_binary.seek(0)
                thumbnail = discord.File(fp=image_binary,filename="image.jpg")
            with BytesIO(req.get(ilust['data']['user_img'], headers=headers).content) as image_binary_user:
                image_binary.seek(0)
                user_image = discord.File(fp=image_binary_user, filename="user.jpg")
            embed=discord.Embed(title=ilust['data']['title'], url="https://pixiv.net/artworks/"+str(ilust['data']['id']), description=ilust['data']['caption'], color=0x1e00ff)
            embed.set_author(name=ilust['data']['user'], url="https://pixiv.net/users/"+str(ilust['data']['user_id']), icon_url="attachment://user.jpg")
            embed.set_image(url="attachment://image.jpg")
            embed.add_field(name="ID Illustrator", value=ilust['data']['id'], inline=False)
            embed.add_field(name="Page Count", value=ilust['data']['page'], inline=True)
            embed.add_field(name="Type", value=ilust['data']['type'], inline=True)
            embed.add_field(name="Tags", value=f'\n'.join(str(x) for x in ilust['data']['tag']), inline=False)
            await ctx.send(files=[thumbnail, user_image], embed=embed)
            json_file.close()
    else:
        with open('option/option.json') as user_token:
            token_data = json.load(user_token)
            tokens = get_token(token_data['username'], token_data['password'])
        
        json_data = json.loads(tokens)
        ilust = get_ilust(data, json_data['data']['access_token'])
        headers = {
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Dest': 'document',
                    'Referer': 'https://pixiv.net'
                }   
        with BytesIO(req.get(ilust['data']['image'], headers=headers).content) as image_binary:
            image_binary.seek(0)
            thumbnail = discord.File(fp=image_binary,filename="image.jpg")
        with BytesIO(req.get(ilust['data']['user_img'], headers=headers).content) as image_binary_user:
            image_binary.seek(0)
            user_image = discord.File(fp=image_binary_user, filename="user.jpg")
        
        embed=discord.Embed(title=ilust['data']['title'], url="https://pixiv.net/artworks/"+str(ilust['data']['id']), description=ilust['data']['caption'], color=0x1e00ff)
        embed.set_author(name=ilust['data']['user'], url="https://pixiv.net/users/"+str(ilust['data']['user_id']), icon_url="attachment://user.jpg")
        embed.set_image(url="attachment://image.jpg")
        embed.add_field(name="ID Illustrator", value=ilust['data']['id'], inline=False)
        embed.add_field(name="Page Count", value=ilust['data']['page'], inline=True)
        embed.add_field(name="Type", value=ilust['data']['type'], inline=True)
        embed.add_field(name="Tags", value=f'\n'.join(str(x) for x in ilust['data']['tag']), inline=False)
        
        await ctx.send(files=[thumbnail, user_image], embed=embed)
        #await ctx.send(f"""Ilust {ilust['data']['id']}, with title {ilust['data']['title']} by {ilust['data']['user']}""")
        
# run bot
sched_new.start()
with open('option/option.json') as option:
    bot_token = json.load(option)
    client.run(bot_token['bot_token'])
