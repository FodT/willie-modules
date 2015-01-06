# coding=utf8
"""
triggerwarning.py - Willie trigger phrase module, 2014

define trigger words and phrases for general fun and amusement
"""
from __future__ import unicode_literals
from collections import defaultdict
from willie.module import commands, rule, example

import json
import random
import re
import os
import threading

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
    fn = 'triggerwarning_dict.json'
    self.dict_filename = os.path.join(self.config.dotdir, fn)
    if not os.path.exists(self.dict_filename):
        try:
            f = open(self.dict_filename, 'w')
        except OSError:
            pass
        else:
            f.write('{}')
            f.close()

    self.memory['triggerwarning_lock'] = threading.Lock()

    if hasattr(self.config, 'triggerwarning'):
        self.trigger_probability = float(self.config.triggerwarning.trigger_probability)
    self.memory['triggerwarning_dict'] = loadTriggers(self.dict_filename, self.memory['triggerwarning_lock'])

def loadTriggers(fn, lock):
    lock.acquire()
    with open(fn) as f:
        result = defaultdict(list, json.load(f))
    lock.release()
    return result

@commands('releasetrigger')
@example('.releasetrigger keyword')
def release_trigger(bot, trigger):
    """Forget phrases for stated trigger (admin only)"""
    if not trigger.admin:
        return
    if not trigger.group(2):
        bot.say(".releasetrigger <keyword> - removes all phrases for that keyword")
        return
    else:
        trigger_key = trigger.group(2).strip().lower()
        if trigger_key in bot.memory['triggerwarning_dict']:
            bot.memory['triggerwarning_dict'].pop(trigger_key, None)
            save_trigger_dict(bot.dict_filename, bot.memory['triggerwarning_dict'], bot.memory['triggerwarning_lock'])
            bot.reply('trigger \'' + trigger_key + '\' removed')
        else:
            bot.reply('nothing to remove')


@commands('trigger')
@example('.trigger (keyword) (hark! what light through yonder window breaks?)')
def trigger_def(bot, trigger):
    """Define a new trigger phrase (admin only)"""
    usage = ".trigger (key phrase) (phrase to use) - include parenthesis - define a new trigger phrase."
    if not trigger.admin:
        return
    if not trigger.group(2):
        bot.say(usage)
        return
    else:
        matches = re.findall(r'\((.+?)\)',trigger.group(0).strip())
        if len(matches) is 2:
            key_phrase = matches[0].lower()
            bot.memory['triggerwarning_dict'][key_phrase].append(matches[1])
            save_trigger_dict(bot.dict_filename, bot.memory['triggerwarning_dict'], bot.memory['triggerwarning_lock'])
            bot.reply('saved. ')
        else:
            bot.say(usage)
            return

@commands('listtriggers')
def list_triggers(bot, trigger):
    """List defined trigger phrases (admin only)"""
    if not trigger.admin:
        return
    if len(bot.memory['triggerwarning_dict'].keys()):
        bot.reply("I have trigger phrases defined for the following phrases: " + ", ".join(bot.memory['triggerwarning_dict'].keys()))
    else:
        bot.reply("I have no trigger phrases defined!")


@rule('[^.].*')
def didYouHearThat(bot, trigger):
    global trigger_probability
    if bot.nick is trigger.nick:
        return
    for phrase in bot.memory['triggerwarning_dict']:
        if phrase in trigger.lower():
            if random.random() < trigger_probability:
                bot.say(random.choice(bot.memory['triggerwarning_dict'][phrase]))
            return

def save_trigger_dict(fn, data, lock):
    lock.acquire()
    with open(fn, 'w') as f:
        json.dump(data, f)
    lock.release()
