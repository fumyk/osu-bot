import requests, telebot
import sys, getpass, json
from telebot import types
from pprint import pprint

modelist = [{'n':'0', 'm':'osu!'},{'n':'1', 'm':'Taiko'},{'n':'2', 'm':'Catch the Beat'},{'n':'3', 'm':'osu!mania'}]

r404 = types.InlineQueryResultArticle(
        id="5", 
        title="Nothing was found, sorry",
        input_message_content=types.InputTextMessageContent(message_text="*( ͡° ͜ʖ ͡°)*", parse_mode="Markdown", disable_web_page_preview=True)
        )
helptext = '''Inline mode only !
*Usage:*
Type `@osuibot <osu! username or id>` in draft

*Author:* @fumycat
*Source:* https://github.com/fumycat/osu-bot
'''

osutoken = getpass.getpass('osutoken:')
bottoken = getpass.getpass('bottoken:')

# osutoken = sys.argv[1]
# bottoken = sys.argv[2]

bot = telebot.TeleBot(bottoken)
pprint(bot.get_me())
with open('country.json') as code:    
    county_list = json.load(code)

@bot.message_handler(content_types=["text"])
def sendhelp(message):
    bot.send_message(chat_id=message.chat.id, text=helptext, parse_mode='Markdown', disable_web_page_preview=True)
    print('Help sent')

@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):
    results = []
    print(query.query)
    payload = {'k': osutoken, 'u': query.query}
    check_request = requests.get('https://osu.ppy.sh/api/get_user', params=payload)
    check_json = check_request.json()
    # check user 404
    if check_json == []:
        results.append(r404)
        bot.answer_inline_query(query.id, results)
        return
    # check for other error(like None)
    errorlevel = parse(check_json, True)
    if errorlevel == 1:
        results.append(r404)
    else:
        for int in [0, 1, 2, 3]:
            mint = int
            true_payload = {'k': osutoken, 'u': query.query, 'm': str(mint)}
            true_request = requests.get('https://osu.ppy.sh/api/get_user', params=true_payload)
            true_json = true_request.json()
            modename = minttomode(mint)
            accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id, playcount = parse(true_json, False)
            # From text
            try:
                text = formtext(username, mint, pp_rank, pp_country_rank, pp_raw, level, accuracy, count_rank_ss, count_rank_s, count_rank_a, user_id, country, playcount)
            except TypeError:
                results.append(r404)
                bot.answer_inline_query(query.id, results)
                return
            # Form result
            result = types.InlineQueryResultArticle(
            id= str(mint), 
            title= username,
            description= modename,
            input_message_content= types.InputTextMessageContent(message_text=text, parse_mode="Markdown", disable_web_page_preview=True)
            )
            results.append(result)

    
    bot.answer_inline_query(query.id, results)

def codetoname(t):
    for dict in county_list:
        if dict['Code'] == t:
            return dict['Name']

def minttomode(m):
    for dict in modelist:
        if dict['n'] == str(m):
            return dict['m']
def formtext(username, mint, pp_rank, pp_country_rank, pp_raw, level, accuracy, count_rank_ss, count_rank_s, count_rank_a, user_id, country, playcount):
    country_name = codetoname(country)
    mode_name = minttomode(mint)
    accuracy = accuracy + '%'
    text = '''*%s*(%s)
#%s in world | _#%s in %s_

*PP* - %s
*Level* - %s
*Accuracy* - %s
*Playcount* - %s
*SS* - %s | *S* - %s | *A* - %s
https://new.ppy.sh/u/''' %(username, mode_name, pp_rank, pp_country_rank, country_name, pp_raw, level, accuracy, playcount, count_rank_ss, count_rank_s, count_rank_a)
    text = text + str(user_id)
    return text

def parse(list, need_cheek):
    errorlevel = 0
    accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id, playcount = '', '', '', '', '', '', '', '', '', '', '', ''
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
        playcount = dict['playcount']

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
        errorlevel = 1
    if accuracy == None:
        errorlevel = 1
    if need_cheek == True:
        return errorlevel
    else:
        return accuracy, count_rank_a, count_rank_s, count_rank_ss, country, level, pp_raw, pp_rank, pp_country_rank, username, user_id, playcount


if __name__ == '__main__':
    while 1:
        try:
            print("\nStart...")
            bot.polling(none_stop=True)
        except Exception as e:
            print("Exception")
            print(str(e))
            continue