from io import BytesIO
import discord
from discord import message
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

def preffix(message):
    c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(message.guild.id),))
    prefix = ''.join(c.fetchone())
    return prefix

def get_prefix(client, message):
    global prefix
    c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(message.guild.id),))
    data = c.fetchone()
    if data is None:
        cursor.execute("INSERT INTO "+db_name+" (id, server_name, category_id, category_name, prefix) VALUES(?, ?, ?, ?, ?)", (int(message.guild.id), str(message.guild), int("0"), str(""), str("g/"),))
        db.commit()
        prefix = "g/"
        return prefix
    else:
        c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(message.guild.id),))
        prefix = ''.join(c.fetchone())
        return prefix

client = commands.Bot(command_prefix=get_prefix)

client.remove_command("help")
@client.event
@commands.is_nsfw()
async def on_guild_join(guild):
    cursor.execute("INSERT INTO "+db_name+" (id, server_name, category_id, category_name, prefix) VALUES(?, ?, ?, ?, ?)", (int(guild.id), str(guild), int("0"), str(""), str("g/"),))
    db.commit()

@client.command()
@commands.is_nsfw()
@commands.has_permissions(administrator = True)
async def changeprefix(ctx, prefix):
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

@client.command()
@commands.is_nsfw()
@commands.has_permissions(administrator = True)
async def setprefix(ctx, prefix):
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
    
@client.event
@commands.is_nsfw()
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please pass in all requirements.**')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")
    if isinstance(error, commands.NSFWChannelRequired):
        await ctx.send("**You need run this command on NSFW Channel**")
    raise error

@client.command()
@commands.is_nsfw()
async def help(ctx):
    embed = discord.Embed(title="Nexiamuel Bot",description=f"""
    This bot is to get doujinshi information from nHentai.

    To get start, just send command `{prefix}code <code>`, and the bot will processed the code and will show info of doujinshi

    Please check the command_prefix, Default is g/
    
    __***Command***__

    **nHentai**
    - `code <code>` : Get information of Doujinshi from nHentai
    - `ping` : Get status from Bot
    - `help` : Open this help
    - `view <code>` : View Doujinshi to secret channel
    - `close` : To Close secret channel, must on the right category channel.
    - `random` : Get random code / Gacha.
    - `random <tags>` : Get random code / gacha by Tags
    - `new` : Get latest dujin, updated an hour.
    - `popular` : Get Popular today
    - `tag <tags>` : Get doujinshi based of tags, can be multiple tags, example : `tag english milf`
    - `artist <artist>` : Get doujinshi based of artist
    - `dl <code>` : It will download to pdf
    
    **pixiv**
    - `pixiv <code> / <url>` : Get illustrator from pixiv
    
    **Bot Settings**
    - `changeprefix <prefix> or setprefix <prefix>` : Change bot prefix on this server
    - mention the bot to Get prefix on this server
    - `setreadcategory <category>` : Set category channel to read
    Will add more feature on the future! If there are any problem, please open issues on my github!""" , color=0x00ccff)
    await ctx.send(embed=embed)

@client.event
@commands.is_nsfw()
async def on_ready():
    print("bot is ready")

@client.event
@commands.is_nsfw()
async def on_message(ctx):
    try:
        
        c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(ctx.guild.id),))
        pre  = ''.join(c.fetchone())
        a = ctx.content
        num = int(a.replace(pre,""))
        
        if ctx.content.startswith(pre + str(num)):
            # print(ctx.content)
            embed = get_code(int(''.join(filter(str.isdigit, ctx.content))))
            await ctx.channel.send("Requested by {}".format(ctx.author.mention))
            await ctx.channel.send(embed=embed)
        
    except Exception as e:
        # print(e)
        
        if client.user.mentioned_in(ctx):
            c = cursor.execute("SELECT prefix FROM "+db_name+" WHERE id == ?", (int(ctx.guild.id),))
            pre  = ''.join(c.fetchone())
            await ctx.channel.send(f"My prefix is {pre}")
        else:
            await client.process_commands(ctx)
        pass
    
@tasks.loop(minutes=15)
async def sched_new():
    # print("Disabled")
    await new_upload_code()
    
@sched_new.before_loop
async def before_sched():
    print("Waiting bot to start..")
    await client.wait_until_ready()

@client.command()
@commands.is_nsfw()
async def ping(ctx):
    await ctx.send("Pong")

@client.command(pass_context = True)
@commands.is_nsfw()
async def code(ctx, kode : int):
    """To get information of code from nHentai
    
    """
    # Process
    # print("Processing", kode)
    try:
        embed = get_code(kode)
        
        await ctx.send("Requested by {}".format(ctx.message.author.mention))
        await ctx.send(embed=embed)
    except:
        await ctx.send("Code not found on database, please check again!")
    
    # This is currently not work, so leave this...
    # await ctx.send("Use **g/read 'insert code here'** to Read, or **g/download 'insert code here'** for download as zip")
    # print("Done")

@code.error
@commands.is_nsfw()
async def code_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Wrong code, please use integer only or Check if the code is correct!")
    else:
        print(error)

@client.command()
@commands.is_nsfw()
async def clear(ctx):
    await ctx.channel.purge()

@client.command(pass_context = True)
@commands.is_nsfw()
async def view(ctx, kode : int):
    """Read Doujin from nHentai
    
    """
    print(kode)
    channel = discord.utils.get(ctx.guild.channels, name=str(kode))
    c = cursor.execute("SELECT * FROM "+db_name+" WHERE id == ?", (int(ctx.message.guild.id),))
    try: 
        for data in c.fetchall():
            if data[2] == 0:
                raise ValueError
            else:
                category_id = data[2]
                server_id = data[0]
                category_name = data[3]
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
                            await channel.send("Don't forget close the channel with command close!")
                else:
                    # print("sudah ada")
                    overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    await channel.set_permissions(ctx.author, overwrite=overwrite)
    except:
        await ctx.send(f"Please configure category name to read with {prefix}!")
    
@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
@commands.is_nsfw()
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
@commands.is_nsfw()
async def setreadcategory_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Command missing arguments, need Category name! Please add category to make bot can make channel on category for view nHentai page!")
        await ctx.send("Use setreadcategory <category name>")
        
    else:
        print(error)

@client.command(pass_context = True)
@commands.is_nsfw()
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

    try:
        await message.clear_reactions()
        await message.delete()
    except:
        pass

@client.command(pass_context = True) 
# @commands.is_nsfw()
async def close(ctx):
    """Close Doujinshi channel
    
    """
    # channel = discord.utils.get(ctx.guild.channels, name=str(kode))
    c = cursor.execute("SELECT * FROM "+db_name+" WHERE id == ?", (int(ctx.message.guild.id),))
    try: 
        for data in c.fetchall():
            if data[2] == 0:
                raise ValueError
            else:
                category_id = data[2]
                server_id = data[0]
                category_name = data[3]
            if str(ctx.message.guild.id) == str(server_id):
                name = category_name
                category = discord.utils.get(ctx.guild.categories, name=name)
                #print(category.id)
                if ctx.message.channel.category.id is not category.id:
                    await ctx.send("Wrong channel")
                    #print(ctx.message.channel.category.id)
                else:
                    channel = ctx.message.channel
                    channel = discord.utils.get(ctx.guild.channels, name=str(channel))
                    await channel.delete()
                    break
    except:
        await ctx.send("There is error, please tell dev")

@client.command(pass_context = True)
@commands.is_nsfw()
async def random(ctx, tag: str = None):
    if tag is None:
        randomize = random_id()
        embed = get_code(randomize)
        await ctx.send("Hey {}, You get this:".format(ctx.message.author.mention))
        await ctx.send(embed=embed)
    else :
        mmsss = await ctx.send("Please wait, it might take a while...")
        try:
            kode = await random_id_tag(tag)
            embed = get_code(kode)
            await mmsss.delete()
            await ctx.send("Hey {}, You get this:".format(ctx.message.author.mention))
            await ctx.send(embed=embed)
        except:
            await mmsss.delete()
            await ctx.send("Tag not found, please check again!")
        

@client.command(pass_context = True)
@commands.is_nsfw()
async def popular(ctx):
    msg = await ctx.send("Getting new Popular now")
    kode = await get_popular()
    total, dujin = popular_detail(kode)
    print(len(dujin))
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    await ctx.message.delete()
    await msg.delete()
    message = await ctx.send(embed = embed_popular(dujin, 0, total))
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
            await message.edit(embed = embed_popular(dujin, i, total))
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = embed_popular(dujin, i, total))
        elif str(reaction) == '▶':
            if i < len(dujin)-1:
                i += 1
                await message.edit(embed = embed_popular(dujin, i, total))
        elif str(reaction) == '⏭':
            i = len(dujin)-1
            await message.edit(embed = embed_popular(dujin, i, total))
        elif str(reaction) == cross:
            await message.delete()
        elif str(reaction) == open_book:
            await view(ctx, json.loads(json.dumps(dujin))[i]['id'])
            await message.edit(content="Opened.")
            
        
        try:
            reaction, user = await client.wait_for('reaction_add', timeout = 300.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break

    try:
        await message.clear_reactions()
        await message.delete()
    except:
        pass
    
@client.command(pass_context = True)
@commands.is_nsfw()
async def tag(ctx, *, tags):
    await ctx.message.delete()
    offset = 0
    if ", " in tags:
        keyword = str(tags).replace(", ", "%%")
    elif " " in tags:
        keyword = str(tags).replace(" ", "%%")
    else:
        keyword = str(tags)
    total, temp = tag_search(keyword, offset)
        
    
    # print(keyword)
    # print(temp)
    
    page_tag = 1
    # print(temp)
    
    
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    try:
        message = await ctx.send(embed = embed_tag(temp, 0, page_tag, total))
    except:
        message = await ctx.send("Data not found, check tag again!")
        return
        
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
            
            if offset > 0:
                offset = offset - 25
            i = 0
            
            if page_tag > 1:
                page_tag = page_tag - 1
                total, temp = tag_search(keyword, offset)
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '◀':
            if i > 0:
                i = i - 1
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '▶':
            if i < 24:
                i = i + 1
                await message.edit(embed = embed_tag(temp, i, page_tag, total))
        elif str(reaction) == '⏭':
            offset = offset + 25
            total, temp = tag_search(keyword, offset)
            i = 0
            page_tag = page_tag + 1
            
            # time.sleep(1)
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

    try:
        await message.clear_reactions()
        await message.delete()
    except:
        pass

@client.command(pass_context = True)
@commands.is_nsfw()
async def artist(ctx, *, tags):
    await ctx.message.delete()
    offset = 0
    if ", " in tags:
        keyword = str(tags).replace(", ", "%%")
    if " " in tags:
        keyword = str(tags).replace(" ", "%%")
    else:
        keyword = str(tags)
    
    # print(keyword)
    total, temp = artist_search(keyword, offset)
    
    page_tag = 1
    # print(keyword)
    
    
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    try:
        message = await ctx.send(embed = embed_artist(temp, 0, page_tag, total))
    except:
        message = await ctx.send("Data not found, check tag again!")
        return
        
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
            
            if offset > 0:
                offset = offset - 25
            i = 0
            
            if page_tag > 1:
                page_tag = page_tag - 1
                total, temp = artist_search(keyword, offset)
                await message.edit(embed = embed_artist(temp, i, page_tag, total))
        elif str(reaction) == '◀':
            if i > 0:
                i = i - 1
                await message.edit(embed = embed_artist(temp, i, page_tag, total))
        elif str(reaction) == '▶':
            if i < 24:
                i = i + 1
                await message.edit(embed = embed_artist(temp, i, page_tag, total))
        elif str(reaction) == '⏭':
            offset = offset + 25
            i = 0
            page_tag = page_tag + 1
            total, temp = artist_search(keyword, offset)
            await message.edit(embed = embed_artist(temp, i, page_tag, total))
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
    try:
        await message.clear_reactions()
        await message.delete()
    except:
        pass   

@client.command(pass_context = True)
@commands.is_nsfw()
async def dl(ctx, kode : int):
    msg = await ctx.send("Please wait ...")
    await save_pdf(kode)
    await msg.edit(content = "Uploading ...")
    if ctx.guild.premium_tier == 2:
        await msg.delete()
        await ctx.send(file=discord.File(str(f"../dujin/{kode}.pdf")))
    elif ctx.guild.premium_tier == 3:
        await msg.delete()
        await ctx.send(file=discord.File(str(f"../dujin/{kode}.pdf")))
    else:
        link = f"https://download.ajipw.my.id/{kode}.pdf"
        size = os.path.getsize(f'../dujin/{kode}.pdf')
        await msg.delete()
        await ctx.send("File Size " + str(size/(1024*1024))+" MB")
        await ctx.send("Enjoy! " + str(link))
        
@client.command(pass_context = True)
async def tes(ctx):
    tier = ctx.guild.premium_tier
    print(tier)
    await ctx.send(tier)

# Pixiv Command :

@client.command(pass_context = True)
@commands.is_nsfw()
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
