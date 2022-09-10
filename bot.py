import os
import get_book_data
from pymongo import MongoClient
from telethon import TelegramClient, events


api_id = os.environ['id']
api_hash = os.environ['hash']
token = os.environ['token']
mongouri = ''

bot = TelegramClient('bot', api_id, api_hash)
bot.start(bot_token=token)
bot.parse_mode = 'md'


clt = MongoClient(mongouri)
mydb = clt['main']
coll = mydb['book']

coll.create_index([('Title', 'text')], name='Title')


def parserr(txt):
    txt = txt.split(' ')[1:]
    sz = len(txt)
    txt = ' '.join(txt)
    txt = txt.replace('"', '\\"')
    txt = txt.replace("'", "\\'")
    return txt, sz


@bot.on(events.NewMessage(pattern=r"\/search "))
async def search(event):
    txt = event.raw_text
    txt, sz = parserr(txt)


    if sz>=2:
        cor = coll.find({'$text':{'$search': f'"{txt}"'}})
    else:
        cor = coll.find({'$text':{'$search': txt}})

    sender = await event.get_sender()
    a = ""
    for inf in cor:
        msg = f'**Bookid: {inf["BookID"]}**\nTitle: {inf["Title"]}\nPublisher: {inf["Publisher"]}\nAuthor: {inf["ResTitle"]}\nPlace: {inf["Place"]}\nYear: {inf["YEAR"]}\n---------------------------------------------------\n'
        a += msg

        #cannot send more than 4000 characters so this condition is used
        if len(a) >= 3500:
            await bot.send_message(sender.id, a)
            a = ""

    await bot.send_message(sender.id, a)

@bot.on(events.NewMessage(pattern=r"\/search \""))
async def author_search(event):
    sender = await event.get_sender()
    txt = event.raw_text
    txt = txt.split("\"")
    
    if len(txt)<4:
        await bot.send_message(sender.id, "Please send message correctly")
    
    else:
        ttl = [x for x in coll.find({'$text': {'$search': txt[1]}})]
        auth = [x for x in coll.find({'$text': {'$search': txt[3]}})]
        rtn = []

        for i in range(abs(len(ttl)-len(auth))):
            if ttl[i] in auth:
                rtn.append(ttl[i])
        msg = ""
        for inf in rtn:
            msg += f'**Bookid: {inf["BookID"]}**\nTitle: {inf["Title"]}\nPublisher: {inf["Publisher"]}\nAuthor: {inf["ResTitle"]}\nPlace: {inf["Place"]}\nYear: {inf["YEAR"]}\n---------------------------------------------\n'
        
        await bot.send_message(sender.id, msg)
        

@bot.on(events.NewMessage(pattern=r"\/detail "))
async def detail(event):
    sender = await event.get_sender()
    txt = event.raw_text
    print(f'{txt} !!!!! {sender.username}')
    txt = txt.split(' ')[1:]
    sz = len(txt)
    if sz>1 or sz==0:
        await bot.send_message(sender.id, "Please send message correctly")

    else:
        data = get_book_data.main(txt[0])
        msg = f'**Bookid**: {data["BookID"]}\nAvailable: {data["Available"]}\nReference: {data["Reference"]}\nNot Issued: {data["Not Issued"]}\nIssued: {data["Issued"]}\nLost: {data["Lost"]}\nMissing: {data["Missing"]}\nDamage: {data["Damage"]}\nTotal: {data["Total"]}'
        await bot.send_message(sender.id, "Extracting data it may take some time")
        await bot.send_message(sender.id, msg)

@bot.on(events.NewMessage(pattern=r"\/help"))
async def help(event):
    sender = await event.get_sender()
    msg = 'List of commands:\n"/search {bookname}" to search the book by name\n\'/search "{book_name}" "{author}"\' to search for book by author\n/detail {bookid}" to get detail of the book. You will get book id from search command'
    await bot.send_message(sender.id, msg)

@bot.on(events.NewMessage(pattern=r"\/start"))
async def greet(event):
    sender = await event.get_sender()
    await bot.send_message(sender.id, f"Type /help for help\nSource code https://github.com/anuj66283/birendra-library-bot")

bot.run_until_disconnected()