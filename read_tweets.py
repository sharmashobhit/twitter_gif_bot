from TwitterAPI import TwitterAPI
from PIL import Image
import urllib2 as urllib
import io
import requests
from random import randint
import os
import re
from config import *

directory_path = os.path.dirname(os.path.abspath(__file__))

def get_random_gif(data=[]):
    query_url = "http://api.giphy.com/v1/gifs/search?q={0}&api_key=dc6zaTOxFJmzC"
    temp_url = query_url.format("+".join(data))
    print temp_url
    t = requests.get(temp_url)

    try:
        data = t.json()['data'][randint(0,t.json()['pagination']['count'])]
    except:
        return 404
    URL = data['images']['fixed_height_downsampled']['url']
    gif_path = directory_path+'/images/'+URL.split('/')[-2]+'.gif'
    response = urllib.urlopen(URL)
    temp = response.read()
    with open(gif_path, 'wb') as f:
        f.write(temp)
    return gif_path

def post_image(data, tweet_id, related_users, sender):
    URL = get_random_gif(data)
    message = ""
    for x in related_users:
        message += '@'+str(x)+' '
    if URL == 404:
        message += "Unable to find a gif with those words. Please try again."
        r = api.request('statuses/update', {'status':message, "in_reply_to_status_id":tweet_id})
    else:
        im = open(URL, 'r')
        r = api.request('media/upload', files=dict(media=im))
        if r.status_code == 200:
            media_id = r.json()['media_id']
            r = api.request('statuses/update', {'status':message, "media_ids":media_id, "in_reply_to_status_id":tweet_id})
    print "Done"

api = TwitterAPI(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
r = api.request('statuses/filter', {'track':'@_gifbot_'})
for item in r:
    text = item['text']
    s = text.split('@_gifbot_ ')[1].split('.')[0]
    s = re.sub("[^\w]", " ",  s).split()
    related_users = [x['screen_name'] for x in item['entities']['user_mentions']]
    sender = item['user']['screen_name']
    related_users.append(sender)
    if '_gifbot_' in related_users:
        related_users.remove('_gifbot_')
    tweet_id = item['id']
    post_image(s, tweet_id, related_users, sender)