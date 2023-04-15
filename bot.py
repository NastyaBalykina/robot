import telebot
from telebot import types
import random
import time

from paho.mqtt import client as mqtt_client, publish

bot = telebot.TeleBot('***')

broker = 'localhost'
port = 1883
topic = "tgbot"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
msgpost = None

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg = f"messages: {msgpost}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def mqttpost():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, "Напиши /menu")
    elif message.text == '/menu':
        keyboard = types.InlineKeyboardMarkup()  # клавиатура
        key_pivo = types.InlineKeyboardButton(text='Будешь пиво?', callback_data='pivo')
        keyboard.add(key_pivo)
        question = 'Привет!'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        keyboard = types.InlineKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text='1', callback_data='1')
        keyboard.add(key_1)
        key_2 = types.InlineKeyboardButton(text='2', callback_data='2')
        keyboard.add(key_2)
        key_3 = types.InlineKeyboardButton(text='3', callback_data='3')
        keyboard.add(key_3)
        key_4 = types.InlineKeyboardButton(text='4', callback_data='4')
        keyboard.add(key_4)
        question = 'Скажи номер места'
        bot.send_message(call.from_user.id, text=question, reply_markup=keyboard)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Ты не знаешь, от чего отказываешься')
    elif call.data == "pivo":
        keyboard = types.InlineKeyboardMarkup()  # клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Хочу пиво!'
        bot.send_message(call.from_user.id, text=question, reply_markup=keyboard)
    elif call.data == "1":
        bot.send_message(call.from_user.id, "Место 1, уже бегу!")
        msgpost == "1"
        mqttpost()
    elif call.data == "2":
        bot.send_message(call.from_user.id, "Место 2, уже бегу!")
        msgpost == "2"
        mqttpost()
    elif call.data == "3":
        bot.send_message(call.from_user.id, "Место 3, уже бегу!")
        msgpost == "3"
        mqttpost()
    elif call.data == "4":
        bot.send_message(call.from_user.id, "Место 4, уже бегу!")
        msgpost == "4"
        mqttpost()

bot.polling(none_stop=True, interval=0)
