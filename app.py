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

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from script.auth import *
from script.pixiv import *
from script.nhentai import *

client = commands.Bot(command_prefix='g/')
client.remove_command("help")

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
    
    Will be add more feature!""" , color=0x00ccff)
    await ctx.send(embed=embed)

@client.event
async def on_ready():
    print("bot is ready")


    
    # scheduler = BackgroundScheduler(daemon=True)
    # scheduler.add_job(threaded, 'interval', hours=1)
    # scheduler.start()
    
    # b = BackgroundScheduler(daemon=True)
    # b.add_job(threaded, 'interval', seconds=1)
    # b.start()
    # time.sleep(2)
    # b.shutdown()

@tasks.loop(hours=1)
async def sched_new():
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
    channel = discord.utils.get(ctx.guild.channels, name=str(kode))
    with open("option/server.json", 'r') as f:
        temp = json.load(f)
    if channel is None:
        guild = ctx.guild
        for code in temp:
            if str(ctx.message.guild.id) == str(code['server_id']):
                name = code['channel_read_name']
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
                        break
        
        
    else:
        # print("sudah ada")
        overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        await channel.set_permissions(ctx.author, overwrite=overwrite)

@client.command(pass_context = True)
async def setreadcategory(ctx, *, channel):
    try:
        try:
            with open('option/server.json') as f:
                temp = json.load(f)
        except :
            temp=[]
            pass
            
        x = 0
        channel_name = discord.utils.get(ctx.guild.categories, name=channel)
        new_data = []
        try:
            for entry in temp:
                if entry['server_id'] == ctx.message.guild.id:
                    s_id = entry['server_id']
                    s_name = entry['server_name']
                    new_data.append({'server_id': s_id, 'server_name': s_name, 'channel_read_id': channel_name.id, 'channel_read_name': str(channel_name)})
                    x+=1
                                
                elif entry['server_id'] != ctx.message.guild.id:
                    x == 0
                    new_data.append(entry)
                    
                else: 
                    x+=1
                    new_data.append(entry)
        except:
            s_id = ctx.message.guild.id
            s_name = ctx.message.guild.name
            new_data.append({'server_id': s_id, 'server_name': s_name, 'channel_read_id': channel_name.id, 'channel_read_name': str(channel_name)})
        with open('option/server.json', "w") as f:
            json.dump(new_data, f, indent=4)  
            
        if x == 0:
            server = {}
            server['server_id'] = ctx.message.guild.id
            server['server_name'] = ctx.message.guild.name
            server['channel_read_id'] = channel_name.id
            server['channel_read_name'] = str(channel_name)
            temp.append(server)
            with open('option/server.json', "w") as f:
                json.dump(temp, f, indent=4)
        await ctx.send(f"Category **{channel}** has been set to read Doujinshi")
    except AttributeError:
        await ctx.send("Please check the category name")
    except Exception:
        await ctx.send("The are error ask bot owner mistake or open Issues in github!")
        
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
    with open("option/nhentai_new.json", 'r', encoding='utf-8') as f:
        temp = json.load(f)
    kode = 0
    await b_text.delete()
    
    # pages = [page1, page2, page3]
    cross = "\U0000274C"
    open_book = "\U0001F4D6"
    message = await ctx.send(embed = pages(0))
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
            await message.edit(embed = pages(i))
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages(i))
        elif str(reaction) == '▶':
            if i < len(temp)-1:
                i += 1
                await message.edit(embed = pages(i))
        elif str(reaction) == '⏭':
            i = len(temp)-1
            await message.edit(embed = pages(i))
        elif str(reaction) == cross:
            await message.delete()
        elif str(reaction) == open_book:
            await view(ctx, temp[i]['id'])
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
