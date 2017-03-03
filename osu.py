import os
import json
from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler

from pprint import pprint

token = os.environ.get('TOKEN')
appname = os.environ.get('APPNAME')
osu_token = os.environ.get('OSU')
port = int(os.environ.get('PORT', '5000'))

updater = Updater(token)
updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(appname, token))

mode_list = {0: 'osu!',
             1: 'Taiko',
             2: 'Catch the Beat',
             3: 'osu!mania'}

with open('country.json') as code:
    country_list = json.load(code)

not_found = [
    InlineQueryResultArticle(id=uuid4(),
                             title="Nothing was found",
                             input_message_content=InputTextMessageContent('( ͡° ͜ʖ ͡°)', parse_mode="Markdown"))]

help_text = '''*Usage:*
Type `@osuibot <osu! username or id>` in draft

*Author:* @fumycat
*Source:* https://github.com/fumycat/osu-bot
'''


def start(bot, update):
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


def inline_handler(bot, update):
    results = []
    for index, mode in mode_list.items():
        print(index, mode)
        query = ''
        request = requests.get('https://osu.ppy.sh/api/get_user', params={'k': osu_token, 'u': query, 'm': index})
        response = request.json()
        pprint(response)
        if not response:
            update.inline_query.answer(not_found)

        try:
            acc, ranks_a, ranks_s, ranks_ss, c, lvl, pp, pp_rank, pp_c_rank, username, u_id, plays = parse(response[0])
            text = format_response(username, mode, pp_rank, pp_c_rank, pp, lvl, acc, ranks_ss,
                                   ranks_s, ranks_a, u_id, c, plays)
            results.append(
                InlineQueryResultArticle(id=uuid4(),
                                         title=username,
                                         description=mode,
                                         input_message_content=InputTextMessageContent(text, parse_mode='Markdown')))
        except Exception as e:
            print(str(e))
    if not results:
        update.inline_query.answer(not_found)
    update.inline_query.answer(results)


def format_response(username, mode, pp_rank, pp_country_rank, pp_raw, level, accuracy, count_rank_ss, count_rank_s,
                    count_rank_a, user_id, country, playcount):
    return '''*{}*({})
#{} in world | _#{} in {}_

*PP* - {}
*Level* - {}
*Accuracy* - {}%
*Playcount* - {}
*SS* - {} | *S* - {} | *A* - {}
https://new.ppy.sh/u/{}'''.format(username, mode, pp_rank, pp_country_rank, country_list[country], pp_raw, level,
                                  accuracy, playcount,
                                  count_rank_ss, count_rank_s, count_rank_a, str(user_id))


def parse(l):
    accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id, playcount = '', '', '', '', '', '', '', '', '', '', '', ''
    for d in l:
        accuracy = d['accuracy']
        count_rank_a = d['count_rank_a']
        count_rank_s = d['count_rank_s']
        count_rank_ss = d['count_rank_ss']
        country = d['country']
        level = d['level']
        pp_raw = d['pp_raw']
        pp_rank = d['pp_rank']
        pp_country_rank = d['pp_country_rank']
        username = d['username']
        user_id = d['user_id']
        playcount = d['playcount']

    try:
        accuracy = float(accuracy)
        level = float(level)
        pp_raw = float(pp_raw)
        accuracy = "{0:.2f}".format(accuracy)
        level = "{0:.0f}".format(level)
        pp_raw = "{0:.0f}".format(pp_raw)
        accuracy = str(accuracy)
        level = str(level)
        pp_raw = str(pp_raw)
    except TypeError:
        return False
    return accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id, playcount


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', start))
updater.dispatcher.add_handler(InlineQueryHandler(inline_handler))

updater.idle()
