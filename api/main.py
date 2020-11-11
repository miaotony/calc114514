#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Calc 114514
Flask API 

@Author: MiaoTony
@CreateTime: 20201109
@UpdateTime: 20201112
"""

from .secret import *
import os
import logging
import time
import re
import telebot
from telebot import types
from flask import Flask, Response, request, abort, jsonify
from flask_cors import CORS
import urllib.parse
from uuid import uuid4

os.chdir(os.path.dirname(__file__))

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, supports_credentials=True)  # allow CORS

re_digit = re.compile(r'^\d+$')


@app.after_request
def after_request(temp_response):
    """
    after a request.
    """
    print("\033[33m#######################################\033[0m")
    return temp_response


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return """Meow~~<br />
<b>Under construction...</b>
<br /><br />
<a href="https://t.me/calc114514bot" target="_blank">@calc114514bot</a>"""


@app.route('/api', methods=['GET', 'POST'])
def api_index():
    return Response("Meow API here~~", mimetype="text/html")


@app.route('/api/test', methods=['GET', 'POST', 'HEAD'])
def api_test():
    """
    API test
    """
    print('\033[33m[INFO] API test!\033[0m')
    url = request.url
    print(url)
    print(urllib.parse.unquote(url))
    raw_data = request.get_data().decode('utf-8')
    print(raw_data)
    print("------------------------------------")
    print(bot.get_me())
    return "OK!\n" + str(raw_data)


@app.route('/api/calc', methods=['GET', 'POST'])
def api_calc():
    """
    Calculate 114514 API
    """
    print('\033[33m[INFO] Calculate 114514 API...\033[0m')
    url = request.url
    print(urllib.parse.unquote(url))
    number = request.args.get('num', '')
    isJson = request.args.get('isJson', '')
    raw_data = request.get_data().decode('utf-8')
    print(raw_data)
    try:
        ans = getans(int(number))
    except:
        ans = 'ERROR!'
    if isJson:
        return jsonify(number=number, answer=ans)
    return ans


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        print(update)
        bot.process_new_updates([update])
        print("------------------------------------")
        time.sleep(0.5)
        return 'OK'
    else:
        abort(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_help_message(message):
    print('Handle command...')
    print(message)
    bot.reply_to(message,
                 ("""Hi, I am Calc114514Bot.
Send me a number, and I will calculate it using `114514` and `+-*/%~|^`.
The number should be `0 <= number <= 999999` at this stage.
See also: USTC Hackergame 2020 超精巧的数字论证器."""),
                 parse_mode='Markdown')


# Handle all messages with digits
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    number = message.text.strip()
    if re_digit.findall(number):
        try:
            number_int = int(number)
            ans = getans(number_int)
            bot.reply_to(message, ans)
        except Exception as e:
            print(e)
            # bot.reply_to(message, message.text)
    print(message.text)


# Handle inline query
@bot.inline_handler(lambda query: re_digit.findall(query.query.strip()))
def query_text(inline_query):
    number = inline_query.query.strip()
    print(number)
    try:
        number_int = int(number)
        ans = getans(number_int)
        r = types.InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"Calculate {number}...",
            input_message_content=types.InputTextMessageContent(ans))
        r2 = types.InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"Calculate {number} with original number...",
            input_message_content=types.InputTextMessageContent(f"{number} = {ans}"))
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e:
        print(e)


def getans(number):
    """
    Get the answer using `114514` & `-~`, `~-`.
    参考官方 WriteUp，基于十进制分解实现，支持6位及以下数字
    https://github.com/USTC-Hackergame/hackergame2020-writeups/blob/master/official/%E8%B6%85%E7%B2%BE%E5%B7%A7%E7%9A%84%E6%95%B0%E5%AD%97%E8%AE%BA%E8%AF%81%E5%99%A8/README.md
    """
    jz = 10
    s = []
    e = "114514"
    for c in e[:1]:
        s.append("~-" * (int(c)) + c)  # value is zero
    for c in e[1:]:
        s.append("-~" * (jz - int(c)) + c)  # value is jz
    ans = ""
    for i in range(len(e)):
        digit = (number // (jz ** (len(e) - 1 - i))) % jz
        ans = "(" + ans + "*" + s[i] + ")" if i > 0 else s[i]
        ans = "-~" * digit + ans
    return ans


if __name__ == '__main__':
    print(bot.get_me())
    app.run(host=WEBHOOK_LISTEN, debug=False)
