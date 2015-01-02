# coding=utf8
"""
triggerwarning.py - Willie trigger phrase module, 2014

define trigger words and phrases for general fun and amusement
"""
from __future__ import unicode_literals
from collections import defaultdict
from willie.module import commands, rule

import json
import random
import re

trigger_probability = 0.5


def configure(config):
    """
    | [triggerwarning]			| example 	| purpose 				|
    | ------- 					| ------- 	| -------				|
    | trigger_probability     	| 0.5  		| Trigger probability	|
    """
    if config.option('Configure triggerwarning module', False):
        config.add_section('triggerwarning')
        config.interactive_add('triggerwarning', 'trigger_probability', 'Trigger probability, 0.0 - 1.0', '0.5')


def setup(self):
    global trigger_probability
    try:
        with open('triggerwarning_dict.json') as f:
            self.memory['triggerdict'] = defaultdict(list, json.load(f))
    except IOError:
        self.memory['triggerdict'] = defaultdict(list)
        save_trigger_dict(self)
    if hasattr(self.config, 'triggerwarning'):
        trigger_probability = float(self.config.triggerwarning.trigger_probability)
        
	
@commands('releasetrigger')
def release_trigger(bot, trigger):
    if not trigger.group(2):
        bot.say(".releasetrigger <keyword> - removes all phrases for that keyword")
        return
    else:
        trigger_key = trigger.group(2).strip().lower()
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
        trigger_key = trigger_sequence[0].lower()
        trigger_phrase = trigger_sequence[2]
        bot.memory['triggerdict'][trigger_key].append(trigger_phrase)
        save_trigger_dict(bot)
        bot.reply('saved. ')

@rule('[^.].*')
def didYouHearThat(bot, trigger):
    global trigger_probability
    if bot.nick is trigger.nick:
        return
    whole_word_regex = r"([\w][\w]*'?\w?)"
    for word in re.compile(whole_word_regex).findall(trigger.lower()):
        if word in bot.memory['triggerdict']:
            if random.random() < trigger_probability:
                bot.say(random.choice(bot.memory['triggerdict'][word]))
            return

def save_trigger_dict(bot):
    with open('triggerwarning_dict.json', 'w') as f:
        json.dump(bot.memory['triggerdict'], f)

