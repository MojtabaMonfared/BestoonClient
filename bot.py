# -*- coding: utf-8 -*-
# Author: @MojtabaMonfared

import redis
import sys
import telebot
import json
import re
import requests
import urllib
import subprocess
import os
from telebot import types
db = redis.StrictRedis(host='localhost', port=6379, db=0)

HEADER = {'Host': 'bestoon.ir',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '78',
    'Cookie': '__cfduid=d31104ec548187f653d598a3481b935e91483530536',
    'Connection': 'keep-alive'
}


stats_message = """{name} عزیز

📊 وضعیت شما تا به الان به این صورت است:

🔷 کل مقدار پول خرج شده: {sum_1}

🔶 تعداد دفعات: {num_1}
➖ ➖➖➖➖➖➖➖➖➖

🔷 کل مقدار پول دریافتی: {sum_2}

🔶 تعداد دفعات: {num_2}""".decode('utf-8')


Settingsmarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
Settingsmarkup.add(types.KeyboardButton("تعویض توکن 🔄"))
Settingsmarkup.add(types.KeyboardButton("برگشت"))


markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(types.KeyboardButton("ثبت درآمد جدید ⬇️"))
markup.add(types.KeyboardButton("ثبت خرج جدید ⬇️"))
markup.add(types.KeyboardButton("وضعیت 🔃"))
markup.add(types.KeyboardButton("تنظیمات ⚙"))

RegisterTokenMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
RegisterTokenMarkup.add(types.KeyboardButton("ثبت توکن 📍"))

siteURL = 'http://bestoon.ir/'
registersiteURL = 'http://bestoon.ir/accounts/register'
githubrepoURL = 'https://github.com/jadijadi/bestoon'

token = '181062749:AAHSsvGZ0pB_V82H8-8bX5UU1nlNAYbJczg'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def StartHelp(message):
	if db.get('token-{}'.format(message.from_user.id)) != None:
		text_1 = """سلام! 👋🏼

بستون یک پروژه اس که قدم به قدم توش سعی می کنیم سیستمی درست کنیم که می شه خرج و دخل رو باهاش نگه داشت. فعلا در ابتدای راهیم و برای استفاده ازش عملا باید یک گیک علاقمند باشی. 😊

برای باز کردن اکانت به [صفحه رجیسترشدن در سایت بستون](http://bestoon.ir/accounts/register) برین و برای اطلاعات بیشتر مراجعه بکنین به [گیت هاب پروژه](https://github.com/jadijadi/bestoon)

ربات غیر رسمی سایت بستون! نوشته شده و منتشر شده به صورت آزاد.

❗️برای کسب اطلاعات بیشتر به [گیتهاب پروژه](http://github.com/MojtabaMonfared/BestoonClient) مراجعه کنید

برای شروع از کیبورد استفاده کنید""".format(registersiteURL=registersiteURL,githubsiteURL=githubrepoURL,)
		bot.send_message(message.from_user.id, text_1, parse_mode="Markdown", reply_markup=markup)
	else:
		bot.send_message(message.chat.id, "ابتدا توکن خودرا ثبت کنید 🚫", reply_markup=RegisterTokenMarkup)


@bot.message_handler(func=lambda message: True)
def messageHandler(message):
	if message.text == "ثبت توکن 📍".decode('utf-8'):
		msgRegister = bot.send_message(message.chat.id, "توکن 48 رقمی خودرا وارد کنید:")
		bot.register_next_step_handler(msgRegister, handleToken)
	elif message.text == "وضعیت 🔃".decode('utf-8'):
		token = db.get('token-{}'.format(message.from_user.id))
		payload = {"token": "{}".format(str(token))}
		req = requests.post(siteURL+'q/generalstat/', data=payload, headers=HEADER)
		req_json = req.json()
		expense = req_json["expense"]
		income = req_json["income"]
		# Request will req to site with user token
		bot.send_message(message.chat.id, stats_message.format(name=message.from_user.first_name,sum_1=expense["amount__sum"], num_1=expense["amount__count"], sum_2=income["amount__sum"], num_2=income["amount__count"]))
	elif message.text == "ثبت درآمد جدید ⬇️".decode('utf-8'):
		msgIncome = bot.send_message(message.chat.id, "*⃣ برای ثبت یه مبلغ دریافتی جدید ابتدا مبلغ را به صورت اعداد انگلیسی وارد کنید:", reply_markup=types.ReplyKeyboardHide())
		bot.register_next_step_handler(msgIncome, MoneyValueCallback)
	elif message.text == "ثبت خرج جدید ⬇️".decode('utf-8'):
		msgExpense = bot.send_message(message.chat.id, "*⃣ برای ثبت یه خرج جدید ابتدا مبلغ را به صورت اعداد انگلیسی وارد کنید:")
		bot.register_next_step_handler(msgExpense, MoneyValueCallbackEx)
	elif message.text == "تنظیمات ⚙".decode('utf-8'):
		msgSetting = bot.send_message(message.chat.id, """✨ به تنظیمات کاربری خود خوش آمدید

در این مرحله شما میتوانید توکن خودرا عوض کنید""".decode('utf-8'), reply_markup=Settingsmarkup)
	elif message.text == "تعویض توکن 🔄".decode('utf-8'):
		msgChangeToken = bot.send_message(message.chat.id, "توکن جدید را بفرستید:")
		bot.register_next_step_handler(msgChangeToken, ChangeToken)
	elif message.text == "برگشت".decode('utf-8'):
		bot.send_message(message.chat.id, "به منوی اصلی بازگشتید", reply_markup=markup)


def handleToken(message):
	token = message.text
	if re.findall(r'\w{48}', token):
		if db.get('token-{}'.format(message.from_user.id)) != None:
			bot.send_message(message.chat.id, "توکن قبلا ثبت شده است دوباره تلاش کنید ", reply_markup=RegisterTokenMarkup)
		else:
			db.set('token-{}'.format(message.from_user.id), token)
			bot.send_message(message.chat.id, "💠 توکن شما با موفقیت ثبت شد حالا میتوانید از طریق کیبورد زیر اقدام به ثبت دخل و خرج خود کنید 😊", reply_markup=markup)
	else:
		bot.send_message(message.chat.id, "توکن اشتباه است دوباره تلاش کنید ", reply_markup=RegisterTokenMarkup)

def MoneyValueCallback(message):
	global money
	money = int(message.text)
	msgIncome1 = bot.send_message(message.chat.id, "🗒 توضیحی درباره این مبلغ بدهید:")
	bot.register_next_step_handler(msgIncome1, MoneyValueCallback1)
def MoneyValueCallback1(message):
	text = message.text.decode('utf-8')
	payload = {
		"token": db.get('token-{}'.format(message.from_user.id)),
		"text": text,
		"amount": money,
	}
	req = requests.post(siteURL+'submit/income', data=payload, headers=HEADER)
	if req.status_code == 200:
		bot.send_message(message.chat.id, "✅ با موفقیت انجام شد!", reply_markup=markup)
	else:
		bot.send_message(message.chat.id, "⛔️ انگار مشکلی بوجود اومده! دوباره تلاش کنید", reply_markup=markup)

def MoneyValueCallbackEx(message):
	global moneyy
	moneyy = int(message.text)
	msgExpense1 = bot.send_message(message.chat.id, "🗒 توضیحی درباره این مبلغ بدهید:")
	bot.register_next_step_handler(msgExpense1, MoneyValueCallbackEx1)

def MoneyValueCallbackEx1(message):
	text = message.text.decode('utf-8')
	payload = {
		"token": db.get('token-{}'.format(message.from_user.id)),
		"text": text,
		"amount": moneyy,
	}
	req = requests.post(siteURL+'submit/expense', data=payload, headers=HEADER)
	if req.status_code == 200:
		bot.send_message(message.chat.id, "✅ با موفقیت انجام شد!", reply_markup=markup)
	else:
		bot.send_message(message.chat.id, "⛔️ انگار مشکلی بوجود اومده! دوباره تلاش کنید", reply_markup=markup)

def ChangeToken(message):
	new_token = message.text
	db.set('token-{}'.format(message.from_user.id), new_token)
	bot.send_message(message.chat.id, "تعویض توکن با موفقیت صورت گرفت ✅")


bot.polling(True)
