import os
import wikipediaapi
from sys import executable
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import ConversationHandler, CommandHandler
import sys
import requests

TOKEN = "825692848:AAH2hGyqjbzcS-AZm_Tcx4DAsBVh5IGNPyE"

def setup_proxy_and_start(token, proxy=True):
    address = "aws.komarov.ml"
    port = 1080
    username = "yandexlyceum"
    password = "yandex"
    try:

        updater = Updater(token, request_kwargs={'proxy_url': f'socks5://{address}:{port}/',
                                                 'urllib3_proxy_kwargs': {'username': username,
                                                                          'password': password}} if proxy else None)
        print('Proxy - OK!')
        main(updater)
    except RuntimeError:
        sleep(1)
        os.system(f'{executable} -m pip install pysocks --user')
        exit(0)

a = open('cities.txt')
b = a.read().split('\n')
a.close()
k = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
cities = {}
for i in k:
    cities[i] = []
for i in b:
    cities[i[0]].append(i)
    
def stop(bot, update, user_data):
    update.message.reply_text('Было интересно поиграть!')
    update.message.reply_text('Количество ходов: {}'.format(len(user_data['cities'])))
    return ConversationHandler.END

def start(bot, update, user_data):
    update.message.reply_text('Привет!')
    update.message.reply_text('Я бот.')
    update.message.reply_text('Привет!')
    user_data['cities'] = []
    user_data['aim'] = 'А'
    update.message.reply_text('Тебе на А.')
    return 1

def Player_step(bot, update, user_data):
    mess = update.message.text
    if mess in b and user_data['aim'] == mess[0]:
        if mess not in user_data['cities']:
            user_data['lastp'] = mess
            user_data['cities'].append(mess)
            update.message.reply_text('Мой ход!')
            y = answer(bot, update, user_data, mess)
            if y == 5:
                return ConversationHandler.END        
            return 1
        else:
            update.message.reply_text('Хммм...')
            update.message.reply_text('Уже было.')
            update.message.reply_text('Давай ещё раз.')
            return 1 
    update.message.reply_text('Хммм...') 
    update.message.reply_text('Кто-то ошибся.')
    update.message.reply_text('Вряд ли это был я.')
    update.message.reply_text('Давай ещё раз.')
    return 1
 
def answer(bot, update, user_data, mess):
    req = mess[-1].upper()
    if req in 'ЪЬЁЫ':
        req = mess[-2].upper()
        if req in 'ЪЬЁЫ':
            req = mess[-3].upper()
    ans = ''
    for i in cities[req]:
        if i not in user_data['cities']:
            ans = i
            break
    if ans != '':
        user_data['lastk'] = ans
        update.message.reply_text(ans)
        k = ans[-1].upper()
        if k in 'ЪЬЁЫ':
            k = ans[-2].upper()
            if k in 'ЪЬЁЫ':
                k = ans[-3].upper()
        user_data['cities'].append(ans)
        user_data['aim'] = k
        update.message.reply_text('Тебе на {}'.format(k))
    else:
        update.message.reply_text('Было интересно поиграть!')
        update.message.reply_text('Количество ходов: {}'.format(len(user_data['cities'])))
        return 5
        
def skip(bot, update, user_data):
    y = answer(bot, update, user_data, user_data['lastk'])
    if y == 5:
        return ConversationHandler.END
    return 1

def info(bot, update, user_data):
    update.message.reply_text('Сначала расскажу про город ' + user_data['lastk'])
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
                language='ru',
                extract_format=wikipediaapi.ExtractFormat.WIKI)
        p_wiki = wiki_wiki.page(user_data['lastk']).text.split('\n')
        for i in p_wiki[:10]:
            try:
                update.message.reply_text(i)
            except:
                pass
        update.message.reply_text('Можешь узнать больше (После окончания игры), написав /wiki ' + user_data['lastk'])
    except:
        update.message.reply_text('Приношу извинения')
        update.message.reply_text('Я не нашел')
        update.message.reply_text('А ещё мне мало платят')
        update.message.reply_text('Мы можете это исправит')
        update.message.reply_text('https://money.yandex.ru/to/410014391030188')
    give_info(bot, update, user_data['lastk'])
    update.message.reply_text('Теперь расскажу про город ' + user_data['lastp'])
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
                language='ru',
                extract_format=wikipediaapi.ExtractFormat.WIKI)
        p_wiki = wiki_wiki.page(user_data['lastp']).text.split('\n')
        for i in p_wiki[:10]:
            try:
                update.message.reply_text(i)
            except:
                pass
        update.message.reply_text('Можешь узнать больше (После окончания игры), написав /wiki ' + user_data['lastp'])
    except:
        update.message.reply_text('Приношу извинения')
        update.message.reply_text('Я не нашел')
        update.message.reply_text('А ещё мне мало платят')
        update.message.reply_text('Мы можете это исправит')
        update.message.reply_text('https://money.yandex.ru/to/410014391030188')
    give_info(bot, update, user_data['lastp'])
    return 1

    
def get_ll_spn(toponym):
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ",".join([toponym_longitude, toponym_lattitude])
    envelope = toponym["boundedBy"]["Envelope"]
    l,b = envelope["lowerCorner"].split(" ")
    r,t = envelope["upperCorner"].split(" ")
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0
    span = "{dx},{dy}".format(**locals())
    return (ll, span)

def give_info(bot, updater, city):
    geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params = {
        "format": "json",
        "geocode": city
    })
    toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    ll, spn = get_ll_spn(toponym)  
    static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&spn=50,50&l=map&pt={ll},flag".format(**locals())
    bot.sendPhoto(
        updater.message.chat.id,
        static_api_request
    )                      

def wiki(bot, update, args, user_data):
    req = ' '.join(args)
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
                language='ru',
                extract_format=wikipediaapi.ExtractFormat.WIKI)
        p_wiki = wiki_wiki.page(req).text.split('\n')
        user_data['req'] = p_wiki
        user_data['i'] = 0
        user_data['maxi'] = len(p_wiki)
        update.message.reply_text('Рассказать ("Да"/"Нет")')
        return 1
    except:
        update.message.reply_text('Приношу извинения')
        update.message.reply_text('Я не нашел')
        update.message.reply_text('А ещё мне мало платят')
        update.message.reply_text('Мы можете это исправит')
        update.message.reply_text('https://money.yandex.ru/to/410014391030188')
    
def wikireader(bot, update, user_data):
    ans = update.message.text
    if ans.lower() == 'да':
        if user_data['i'] != user_data['maxi']:
            for i in range(user_data['i'], min(user_data['i'] + 10, user_data['maxi'] + 1)):
                try:
                    update.message.reply_text(user_data['req'][i])
                except:
                    pass 
            user_data['i'] = i
            update.message.reply_text('Рассказать ещё ("Да"/"Нет")')
            return 1
        else:
            update.message.reply_text('Всё.')
            return ConversationHandler.END
    elif ans.lower() == 'нет':
        return ConversationHandler.END
    else:
        update.message.reply_text('Я вас не понял')
        update.message.reply_text('Повторите пожалуйста')
        return

def wikistop(bot, update):
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_user_data=True)],
 
    states={
        1: [MessageHandler(Filters.text, Player_step, pass_user_data=True)],
        },
    fallbacks=[CommandHandler('stop', stop, pass_user_data=True),
               CommandHandler('skip', skip, pass_user_data=True),
               CommandHandler('info', info, pass_user_data=True)])

ask_handler = ConversationHandler(
    entry_points=[CommandHandler('wiki', wiki, pass_args=True, pass_user_data=True)],
    states={1: [MessageHandler(Filters.text, wikireader, pass_user_data=True)]},
    fallbacks=[CommandHandler('wikistop', wikistop, pass_user_data=True)])

def main(updater):
    dp = updater.dispatcher
    text_handler = conv_handler
    dp.add_handler(text_handler)
    dp.add_handler(ask_handler)  
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    setup_proxy_and_start(token=TOKEN, proxy=True)