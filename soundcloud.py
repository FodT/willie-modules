# coding=utf8
"""
soundcloud.py - Willie Soundcloud Module

http://willie.dfbta.net

This module will respond to .sc and .soundcloud commands and searches soundcloud.
"""
from __future__ import unicode_literals

from willie import web, tools
from willie.module import rule, commands, example, rate
import json
import re
import sys

if sys.version_info.major < 3:
    from HTMLParser import HTMLParser
else:
    from html.parser import HTMLParser


def scget(bot, trigger, uri):
    bytes = web.get(uri)
    result = json.loads(bytes)
    try:
		song_entry = result[0]
    except IndexError:
		return {'link': 'N/A'}  # Empty result

    song_info = {}
    try:
        song_info['link'] = song_entry['permalink_url']	
    except KeyError:
        song_info['link'] = 'N/A'

    try:
        song_info['title'] = song_entry['title']
    except KeyError:
        song_info['title'] = 'N/A'

    #get soundcloud user channel
    try:
        song_info['uploader'] = song_entry['user']['username']
    except KeyError:
        song_info['uploader'] = 'N/A'

    #get upload time in format: yyyy-MM-ddThh:mm:ss.sssZ
    try:
        upraw = song_entry['last_modified']
        #parse from current format to output format: DD/MM/yyyy
        song_info['uploaded'] = '%s/%s/%s' % (upraw[8:10], upraw[5:7], upraw[0:4])
    except KeyError:
        song_info['uploaded'] = 'N/A'

    #get duration in milliseconds, convert to friendly string
    try:
        duration = int(song_entry['duration'])
       
        hours = ((duration / (1000*60*60)) % 24)
        minutes = ((duration / (1000*60)) % 60)
        seconds = (duration / 1000) % 60

	song_info['length'] = '%d:%d:%d' % (hours, minutes, seconds)
    except KeyError:
        song_info['length'] = 'N/A'

    #get listens
    try:
        listens = song_entry['playback_count']
        song_info['listens'] = str('{0:20,d}'.format(int(listens))).lstrip(' ')
    except KeyError:
        song_info['listens'] = 'N/A'

    #get comment count
    try:
        comments = song_entry['comment_count']
        song_info['comments'] = str('{0:20,d}'.format(int(comments))).lstrip(' ')
    except KeyError:
        song_info['comments'] = 'N/A'

    #get likes & dislikes
    try:
        likes = song_entry['favoritings_count']
        song_info['likes'] = str('{0:20,d}'.format(int(likes))).lstrip(' ')
    except KeyError:
        song_info['likes'] = 'N/A'
 
    return song_info

@rate(5)
@commands('sc', 'soundcloud')
@example('.sc never gonna give you up')
def scsearch(bot, trigger):
    """Search Soundcloud"""
    if not trigger.group(2):
        return
    uri = 'http://api.soundcloud.com/tracks?client_id=3639a3c4768be1fdd5a69afea8bbf619&q=' + trigger.group(2) + '&limit=1'
    
    song_info = scget(bot, trigger, uri)
    if song_info is 'err':
        return

    if song_info['link'] == 'N/A':
        bot.reply("Sorry, I couldn't find the song you are looking for")
        return
	
	#combine variables and print
    message =  song_info['title'] + \
              ' | Uploaded: ' + song_info['uploaded'] + \
              ' | Duration: ' + song_info['length'] + \
              ' | ' +  song_info['link'] 
	

    bot.reply(HTMLParser().unescape(message))
