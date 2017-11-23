# -*- coding: utf-8 -*-
from decouple import config
import requests
import json
import sqlite3

token = config('TOKEN')

BASE_URL = 'https://api.telegram.org/bot{}/'.format(token)


class BotFalar:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS items (description text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, item_text):
        stmt = "INSERT INTO items (description) VALUES (?)"
        args = (item_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text):
        stmt = "DELETE FROM items WHERE description = (?)"
        args = (item_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self):
        stmt = "SELECT description FROM items"
        return [x[0] for x in self.conn.execute(stmt)]

    # class BotFalar():
    def get_me(self):
        self.bot = requests.get('{}getme'.format(BASE_URL)).json()
        return self.bot

        # def get_update(self, update_id):
        # self.bot_update = requests.get('{}getupdates?offset={}'.format(BASE_URL, update_id))
        # return json.loads(bot.content)
        # return self.bot_update.json()

    def get_updates(self, offset):
        self.last_update_id = 0
        self.resp = requests.get('{}getUpdates?offset={}&timeout=5'.format(BASE_URL, offset)).json()
        self.result = len(self.resp['result'])
        if self.result >= 1:
            self.last_index = self.resp['result'][self.result - 1]
            self.chat = self.last_index['message']['chat']
            self.last_update_id = self.last_index['update_id']
            self.chat_id = self.chat['id']
            self.first_name = self.chat['first_name']
            self.text = self.last_index['message']['text']
            self.handle_updates()
        return self.last_update_id

    def send_message(self, chat_id, text):
        data = {'chat_id': chat_id, 'text': text}
        self.response = requests.post('{}sendmessage'.format(BASE_URL), data)
        return self.response

    def username(self):
        self.bot_username = requests.get('{}getupdates'.format(BASE_URL)).json()
        return self.bot_username['result'][-1]['message']['from']['username']

    #     def handle_updates(self, last_update_id):
    #         #for update in updates["result"]:
    #         name = self.first_name
    #         text = self.text
    #         chat = self.chat_id
    #         items = self.get_items()
    #         #print(items)
    #         if text == "/lista":
    #             #keyboard = build_keyboard(items)
    #             self.send_message(self.chat_id,"Selecione um item para apagar")
    #         elif text == "/start":
    #             self.send_message(
    #                 self.chat_id,"{},\nBem vindo à sua lista pessoal. Digite um item para adicionar à lista.\n"
    #                 "Digite /lista para ver os itens e se quiser apagá-lo da lista, clique sobre o item.".format(name))
    #         #elif text.startswith("/"):
    #         #     continue
    #         #elif text in items:
    #         #    self.delete_item(text)
    #         #    items = self.get_items()
    #             #keyboard = self.build_keyboard(items)
    #         #    self.send_message(self.chat_id,"Selecione um item para apagá-lo.")
    #         else:
    #             self.add_item(name, text)
    #             items = self.get_items()
    #             message = "\n".join(items)
    #             self.send_message(self.chat_id,message)


    def handle_updates(self):
        #         for update in updates["result"]:
        try:
            text = self.text
            chat = self.chat_id
            items = self.get_items()
            if text in items:
                self.delete_item(text)
                items = self.get_items()
            else:
                self.add_item(text)
                items = self.get_items()
            message = "\n".join(items)
            self.send_message(chat, message)
        except KeyError:
            pass

    def build_keyboard(self, items):
        keyboard = [[item] for item in items]
        self.reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
        return json.dumps(self.reply_markup)


def main():
    yros = BotFalar()
    yros.setup()
    last_id = 0
    while True:

        last_id = yros.get_updates(last_id + 1)
        print("Aguardando mensagens...")
        print(yros.resp)
        # print(last_id)
        # yros.handle_updates()


if __name__ == '__main__':
    main()
