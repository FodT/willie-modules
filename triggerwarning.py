# coding=utf8
"""
triggerwarning.py - Willie trigger phrase module

define trigger words and phrases for general fun and amusement

"""
from __future__ import unicode_literals
from collections import defaultdict
from willie.module import commands, rule

import json
import random

def setup(self):
    try:
        with open('triggerwarning_dict.json') as f:
            self.memory['triggerdict'] = defaultdict(list, json.load(f))
    except IOError:
        self.memory['triggerdict'] = defaultdict(list)
        save_trigger_dict(self)


@commands('releasetrigger')
def release_trigger(bot, trigger):
    if not trigger.group(2):
        bot.say(".releasetrigger <keyword> - removes all phrases for that keyword")
        return
    else:
        trigger_key = trigger.group(2).strip()
        if trigger_key in bot.memory['triggerdict']:
            bot.memory['triggerdict'].pop(trigger_key, None)
            save_trigger_dict(bot)
            bot.reply('trigger \'' + trigger_key + '\' removed')
        else:
            bot.reply('nothing to remove')


@commands('trigger')
def trigger_def(bot, trigger):
    if not trigger.admin:
        return
    if not trigger.group(2):
        bot.say(".trigger <keyword> <phrase> - define a new trigger phrase.")
        return
    else:
        trigger_sequence = trigger.group(2).strip().partition(r' ')
        trigger_key = trigger_sequence[0]
        trigger_phrase = trigger_sequence[2]
        bot.memory['triggerdict'][trigger_key].append(trigger_phrase)
        save_trigger_dict(bot)
        bot.reply('saved. ')

@rule('[^.].*')
def didYouHearThat(bot, trigger):
    if bot.nick is trigger.nick:
        return

    for word in trigger.split(' '):
        if word in bot.memory['triggerdict']:
            bot.say(random.choice(bot.memory['triggerdict'][word]))
            return

def save_trigger_dict(bot):
    with open('triggerwarning_dict.json', 'w') as f:
        json.dump(bot.memory['triggerdict'], f)

