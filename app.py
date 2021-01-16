from io import BytesIO
import discord
from discord.ext import commands
from discord.utils import get
import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import re
import os.path

from requests.sessions import get_auth_from_url
from script.auth import *
from script.pixiv import *


client = commands.Bot(command_prefix='.')
client.remove_command("help")

@client.command()
async def help(ctx):
    embed = discord.Embed(title="Nexiamuel NSFW Bot",description=f"""
    This bot is useful to get doujinshi information from nHentai.

    To get start, just send command `g/code <code>`, and the bot will processed the code and will s>

    __***Command***__

    **nHentai**
    - `g/code <code>` : Get information of Doujinshi from nHentai
    - `g/ping` : Get status from Bot
    - `g/help` : Open this help
    - `g/view <code>` : View Doujinshi to secret channel
    - `g/close` : To Close secret channel, must on the right category channel.
    
    **pixiv**
    - `g/pixiv <code> / <url>` : Get illustrator from pixiv
    
    Will be add more feature!""" , color=0x00ccff)
    await ctx.send(embed=embed)

@client.event
async def on_ready():
    print("bot is ready")

@client.command()
async def ping(ctx):
    await ctx.send("Pong")

@client.command(pass_context = True)
async def code(ctx, *, kode : int):
    """To get information of code from nHentai
    
    """
    # Process
    # print("Processing", kode)
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
async def view(ctx, *, kode : int):
    """Read Doujin from nHentai
    
    """
    channel = discord.utils.get(ctx.guild.channels, name=str(kode))
    if channel is None:
        guild = ctx.guild
        name = 'Coba'
        category = discord.utils.get(ctx.guild.categories, name=name)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await guild.create_text_channel(kode, category=category, overwrites=overwrites)
        channel = discord.utils.get(ctx.guild.channels, name=str(kode))
        
        url = req.get("https://nhentai.net/g/"+str(kode)+"/1").text
        raw = bs(url, 'html.parser')
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
async def close(ctx):
    """Close Doujinshi channel
    
    """
    name = 'Coba'
    category = discord.utils.get(ctx.guild.categories, name=name)
    #print(category.id)
    if ctx.message.channel.category.id is not category.id:
        await ctx.send("Salah channel Cok!")
        #print(ctx.message.channel.category.id)
    else:
        channel = ctx.message.channel
        channel = discord.utils.get(ctx.guild.channels, name=str(channel))
        await channel.delete()

@client.command(pass_context = True) 
async def p_get(ctx, *, data):
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
with open('option/option.json') as option:
    bot_token = json.load(option)
    client.run(bot_token['bot_token'])
