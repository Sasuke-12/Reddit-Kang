from config import bot, subreddit, channel_id, main_channel_id, agent
from telethon import events, Button
import asyncio
import requests
import os
from PIL import Image

# Global variables

reddit = "https://www.reddit.com/r/{}/new.json"
last = {}
max_size = 10 * 1024 * 1024
subreddits = subreddit.split('+')
sleep_time = 60*5

try:
    channel_id = int(channel_id)
except:
    channel_id = channel_id




def get_image_url(feed ,preview_url):
    gallery_url_prefix = 'https://i.redd.it/'

    
    if 'i.redd.it' in preview_url:
        return preview_url
    if 'gallery' in preview_url:
        return gallery_url_prefix + id + '.' + feed['data']['children'][0]['media_metadata'][id]['m'].split('/')[-1]
    
    url = preview_url.split('?')[0]
    url = url.replace('preview', 'i')
    url = url.replace('b.thumbs.redditmedia.com', 'i.redd.it')
    url = url.replace('a.thumbs.redditmedia.com', 'i.redd.it')
    url = url.replace('external-preview.redd.it', 'i.redd.it')
    return url
 

def parse_feed(subreddit):
    url = reddit.format(subreddit)
    feed = requests.get(url, headers={'User-agent': agent}).json()
    if "error" in feed:
        raise Exception(f"error {feed['error']} \nmessage: {feed['message']}")
    if feed['data']['children'][0]['data']['is_video'] is True: 
        return None
    if feed['data']['children'][0]['data']['url'] == last.get(subreddit):
        return None
    
    feed_dict = {
        'title': feed['data']['children'][0]['data']['title'],
        'url': get_image_url(feed, feed['data']['children'][0]['data']['url']),
    }
    last[subreddit] = feed['data']['children'][0]['data']['url']
    
    return feed_dict
    
def new_filename(filename, url):
    garbage = ",\'\"()[]:;{\\/}`"
    for a in garbage:
        if a in filename:
            filename = filename.replace(a, '')
            
    cutout = "cutout in comments"
    filename = filename.replace(cutout, '')
    file_ext = url.split('.')[-1]
    filename = filename + '.' + file_ext
    
    return filename
    


def download_img(img_url, filename:str):
    res = requests.get(img_url)
    if res.status_code != 200:
        return None
    if not os.path.exists('images'):
        os.mkdir('images')

    with open(f"images/{filename}", 'wb') as f:
        f.write(res.content)

def get_thumb(filename):
    if not os.path.exists(f"images/{filename}"):
        return None
    if os.path.getsize(f"images/{filename}") < max_size:
        return None
    img = Image.open(f"images/{filename}")
    img.save(f"images/thumb_{filename}", "JPEG", quality=60)

    return f"images/thumb_{filename}"

def wipe_images():
    if not os.path.exists('images'):
        return
    for file in os.listdir('images'):
        os.remove(f"images/{file}")
    

loop = asyncio.get_event_loop()
async def loop_reddit():
    channel = await bot.get_entity(channel_id)
    while True:
        for subreddit in subreddits:
            try:
                feed = parse_feed(subreddit)
                if feed is None:
                    continue
                
                filename = new_filename(feed['title'], feed['url'])
                download_img(feed['url'], filename)
                
                file_path = f"images/{filename}"
                await bot.send_message(
                            channel, 
                            f"{feed['title']}\n@{main_channel_id}", 
                            file=file_path,
                        )
                await bot.send_message(
                    channel, 
                    f"{feed['title']}\n@{main_channel_id}", 
                    file=file_path, 
                    force_document=True,
                    thumb=get_thumb(filename), 
                    buttons=[Button.inline('approve', b'approve'),Button.inline('reject', b'reject')])
                wipe_images()
                
            except Exception as e:
                wipe_images()
                print(e)
                continue
        print("sleeping")
        await asyncio.sleep(sleep_time)
            
        

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await bot.send_message(event.chat_id, "Bot is Running")

@bot.on(events.CallbackQuery(pattern=b"e1"))
async def emoji1(event):
    data = event.data.decode('utf-8')
    data_split = data.split(':')
    new_count = int(data_split[1]) +1
    await event.edit(buttons=[
        Button.inline(f"❤️ {new_count}", data=f"e1:{new_count}:{data_split[2]}:{data_split[3]}"), 
        Button.inline(f"👍🏻 {data_split[2]}", data=f"e2:{new_count}:{data_split[2]}:{data_split[3]}"), 
        Button.inline(f"👎🏻 {data_split[3]}", data=f"e3:{new_count}:{data_split[2]}:{data_split[3]}")
    ])

@bot.on(events.CallbackQuery(pattern=b"e2"))
async def emoji2(event):
    data = event.data.decode('utf-8')
    data_split = data.split(':')
    new_count = int(data_split[2]) + 1
    await event.edit(buttons=[
        Button.inline(f"❤️ {data_split[1]}", data=f"e1:{data_split[1]}:{new_count}:{data_split[3]}"), 
        Button.inline(f"👍🏻 {new_count}", data=f"e2:{data_split[1]}:{new_count}:{data_split[3]}"), 
        Button.inline(f"👎🏻 {data_split[3]}", data=f"e3:{data_split[1]}:{new_count}:{data_split[3]}")
    ])

@bot.on(events.CallbackQuery(pattern=b"e3"))
async def emoji3(event):
    data = event.data.decode('utf-8')
    data_split = data.split(':')
    new_count = int(data_split[3]) + 1
    await event.edit(buttons=[
        Button.inline(f"❤️ {data_split[1]}", data=f"e1:{data_split[1]}:{data_split[2]}:{new_count}"), 
        Button.inline(f"👍🏻 {data_split[2]}", data=f"e2:{data_split[1]}:{data_split[2]}:{new_count}"), 
        Button.inline(f"👎🏻 {new_count}", data=f"e3:{data_split[1]}:{data_split[2]}:{new_count}")
    ])

@bot.on(events.CallbackQuery)
async def click_handler(event):
    channel = await bot.get_entity(channel_id)
    main_channel = await bot.get_entity(f"t.me/{main_channel_id}")
    message = event.message_id
    user_info = await event.get_sender()

    messages = await bot.get_messages(channel,ids=message)
    message2 = await bot.get_messages(channel,ids=message - 1)

    try: 
        msg_txt = messages.message
    except:
        pass
    if event.data == b'approve':
        await bot.send_message(main_channel,message2,buttons = Button.clear())
        await bot.send_message(main_channel,messages, buttons=[Button.inline("❤️ 0", data="e1:0:0:0"), Button.inline("👍🏻 0", data="e2:0:0:0"), Button.inline("👎🏻 0", data="e3:0:0:0")])
        
        await bot.edit_message(channel,message,f"{msg_txt}\n\nthis message was posted by @{user_info.username}")
    elif event.data == b'reject':
        await bot.edit_message(channel,message,f"{msg_txt}\n\nthis message was rejected by @{user_info.username}")


#,buttons = [Button.inline("❤️ 0", data="e1:0:0:0"), Button.inline("👍🏻 0", data="e2:0:0:0"), Button.inline("👎🏻 0", data="e3:0:0:0")]

loop.run_until_complete(loop_reddit())

bot.start()

bot.run_until_disconnected()
