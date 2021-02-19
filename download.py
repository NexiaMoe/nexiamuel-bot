from sys import argv
import requests as req
from bs4 import BeautifulSoup as bs
import re
import img2pdf
import multiprocessing as mp
from os import path
import os
import io 
def zu(args):
    linkss = args
    link = ''.join(linkss)
    # print(link)
    return content_list(link)

def content_list(link):
    content = []
    a = req.get(link)
    if a.status_code == 404:
        png = link.replace("jpg","png")
        print(png)
        content.append(bytes(req.get(png).content))
    else :
        print(link)
        content.append(bytes(a.content))
    return content

# async with aiohttp.ClientSession() as session:
#     async with session.get("https://nhentai.net/g/"+str(kode)+"/1") as r:
code = argv[1]
if __name__ == '__main__':
    if os.name != 'nt':
        if path.isfile(f'../dujin/{code}.pdf') == True and path.getsize(f'../dujin/{code}.pdf') != 0:
            print("File Exist, Send link download...")
            pass
        else:
            url = req.get(f"https://nhentai.net/g/{code}/1")
            text = url.text
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

            # print(req.get(link[0]).content)
            


            with open(f"../dujin/{code}.pdf", 'wb') as f:
                u = 1
                pool = mp.Pool(4)
                content = pool.imap(zu, zip(link))
                content = [ent for sublist in content for ent in sublist]
                a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
                layout_fun = img2pdf.get_layout_fun(a4inpt)

                print(len(content))
                f.write(img2pdf.convert(content, layout_fun=layout_fun))
    
    else:
        if path.isfile(f'{code}.pdf') == True and path.getsize(f'{code}.pdf') != 0:
            print("File Exist, Send link download...")
            pass
        else:
            url = req.get(f"https://nhentai.net/g/{code}/1")
            text = url.text
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

            # print(req.get(link[0]).content)
            


            with open(f"{code}.pdf", 'wb') as f:
                u = 1
                pool = mp.Pool(4)
                content = pool.imap(zu, zip(link))
                content = [ent for sublist in content for ent in sublist]
                a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
                layout_fun = img2pdf.get_layout_fun(a4inpt)

                print(len(content))
                f.write(img2pdf.convert(content, layout_fun=layout_fun))