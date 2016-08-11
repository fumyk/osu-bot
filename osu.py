import requests
import sys
import telebot
import json
from telebot import types

osutoken = sys.argv[1]
bottoken = sys.argv[2]
bot = telebot.TeleBot(bottoken)
with open('country.json') as code:    
    county_list = json.load(code)

@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    results = []
    payload = {'k': osutoken, 'u': query.query}
    r = requests.get('https://osu.ppy.sh/api/get_user', params=payload)
    pr = r.json()
    if pr == []:
        result = types.InlineQueryResultArticle(
        id="1", 
        title="Nothing was found, sorry",
        input_message_content=types.InputTextMessageContent(message_text="*( ͡° ͜ʖ ͡°)*", parse_mode="Markdown", disable_web_page_preview=True)
    )
    else:
        accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id = parse(pr)
        country_name = codetoname(country)
        text = '''*%s*(%s)
#%s in world | _#%s in %s_

*PP* - %s
*Level* - %s
*Accuracy* - %s
*SS* - %s | *S* - %s | *A* - %s
https://new.ppy.sh/u/''' %(username, country, pp_rank, pp_country_rank, country_name, pp_raw, level, accuracy, count_rank_ss, count_rank_s, count_rank_a)
        text = text + str(user_id)
        result = types.InlineQueryResultArticle(
        id="1", 
        title=username,
        description=country,
        input_message_content=types.InputTextMessageContent(message_text=text, parse_mode="Markdown", disable_web_page_preview=True)
    )

    results.append(result)
    bot.answer_inline_query(query.id, results)
def codetoname(t):
    for dict in county_list:
        if dict['Code'] == t:
            return dict['Name']

def parse(list):
    accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id = '', '', '', '', '', '', '', '', '', '', ''
    for dict in list:
        accuracy = dict['accuracy']
        count_rank_a = dict['count_rank_a']
        count_rank_s = dict['count_rank_s']
        count_rank_ss = dict['count_rank_ss']
        country = dict['country']
        level = dict['level']
        pp_raw = dict['pp_raw']
        pp_rank = dict['pp_rank']
        pp_country_rank = dict['pp_country_rank']
        username = dict['username']
        user_id = dict['user_id']

    accuracy = float(accuracy)
    level = float(level)
    pp_raw = float(pp_raw)
    accuracy = "{0:.2f}".format(accuracy)
    level = "{0:.0f}".format(level)
    pp_raw = "{0:.0f}".format(pp_raw)
    accuracy = str(accuracy)
    level = str(level)
    pp_raw = str(pp_raw)
    return accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id

if __name__ == '__main__':
     bot.polling(none_stop=True)