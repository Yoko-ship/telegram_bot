from flask import Flask,request
import google.generativeai as genai
import telebot
import PIL.Image,os
import requests,json



app = Flask(__name__)

api_token ="7184222356:AAHvafd3do_Ozpfy8kw8CaAI7UC-aC5pmg4"
api_key = "AIzaSyCsbm3paPBslK2g0MW8YwZwD4zpl9H_37Y"



#* конфиг ai
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

#* Обработчик для текстов
#* Можно добавлять и другие обработчики


class Tele_bot:
    def __init__(self,token):
        self.bot = telebot.TeleBot(token)
        self._setup_handler()

    def _setup_handler(self):
        @self.bot.message_handler(content_types=["text"])
        def get_text_message(message):
            if message.text == "Привет":
                self.bot.send_message(message.from_user.id,"Привет,попробуй использовать команду /help") 
            elif message.text == "/help":
                self.bot.send_message(message.from_user.id,"Доступные команды: /ask /create_blog_with_photo /vocabulary /recipe /quote /weather")

            elif message.text == "/create_blog_with_photo":
                self.bot.send_message(message.from_user.id,"Напиши полный путь к фото")
                self.bot.register_next_step_handler(message,self.create_photo)

            elif message.text == "/ask":
                self.bot.send_message(message.from_user.id,"Что ты хочешь узнать ?")
                self.bot.register_next_step_handler(message,self.answer_question)

            elif message.text == "/vocabulary":
                self.bot.send_message(message.from_user.id,"Напишите тему(например спорт,еда и тд) и количество в цифрах ")
                self.bot.register_next_step_handler(message,self.give_vocabulary)
            
            elif message.text == '/recipe':
                self.bot.send_message(message.from_user.id,"Напиши '!рецепт' 'еду' и предпочитаемый язык через пробел")
                self.bot.register_next_step_handler(message,self.give_recipe)

            
            elif message.text == "/weather":
                self.bot.send_message(message.from_user.id,"Введите город")
                self.bot.register_next_step_handler(message,self.weather_info)


            elif message.text == "/quote":
                
                self.response = model.generate_content("Дай великие цитаты умных филосовоф или людей")
                try:
                    self.bot.send_message(message.from_user.id,self.response.text)
                except Exception:
                    self.bot.send_message(message.from_user.id,"Попробуйте ещё раз")

            else:
                self.bot.send_message(message.from_user.id,"Напиши /help /create_blog_with_photo /ask /vocabulary /recipe /quote /weather")



    #* финалли могу бесконечно просить ответ))
    def answer_question(self,message):
        if message.text == "stop":
            self.bot.send_message(message.from_user.id,"Вы приостановили функцию,теперь введите /help")
            try: 
                self.bot.register_next_step_handler(message,self.get_text_message)

            except AttributeError:
                print("")
        else:
            self.userInput = message.text
            self.response = model.generate_content(self.userInput)
            try:
                self.bot.send_message(message.from_user.id,self.response.text)
                self.bot.register_next_step_handler(message,self.answer_question)
            except Exception:
                self.bot.send_message(message.from_user.id,"Попробуйте ещё раз // Для смены темы напишите stop")



    def create_photo(self,message):
        #* Обрабатываем фото
        self.photo = message.text
        if os.path.isabs(self.photo):
            self.img = PIL.Image.open(self.photo)
            self.response = model.generate_content(["Write a short, engaging blog post based on this picture on russian.",self.img],stream=True)
            self.response.resolve()
            try:
                self.bot.send_message(message.from_user.id,self.response.text)
            except Exception:
                self.bot.send_message(message.from_user.id,"Попробуйте ещё раз")
        else:
            self.bot.send_message(message.from_user.id,"Попробуйте ещё раз с полным названием к пути файла")
            
        
    def give_vocabulary(self,message):
        if message.text == "stop":
                    self.bot.send_message(message.from_user.id,"Вы приостановили функцию,теперь введите /help")
                    try: 
                        self.bot.register_next_step_handler(message,self.get_text_message)

                    except AttributeError:
                         print("")
        else:
            try:
                 
                self.userInput = message.text
                self.vocabulary,self.quantity = self.userInput.split()
                self.vocabulary,self.quantity = str(self.vocabulary),int(self.quantity)
                self.response = model.generate_content(f"Дай мне vocabulary на тему{self.vocabulary} на английском с переводом на русский с количеством {self.quantity}",stream=True)
                self.response.resolve()
                self.bot.send_message(message.from_user.id,self.response.text)
                self.bot.register_next_step_handler(message,self.give_vocabulary)
            except ValueError:
                self.bot.send_message(message.chat.id,"Напишите 'vocabulary' и количество в цифрах // Для смены темы напишите stop")
                self.bot.register_next_step_handler(message,self.give_vocabulary)
                

    def give_recipe(self,message):
        if message.text == "stop":
                    self.bot.send_message(message.from_user.id,"Вы приостановили функцию,теперь введите /help")
                    try: 
                        self.bot.register_next_step_handler(message,self.get_text_message)

                    except AttributeError:
                         print("")
        else:
            try:
                 
                self.userInput = message.text
                self.recipe,self.eats,self.language = self.userInput.split()
                self.response = model.generate_content([f"Дай рецепт на еду {self.eats} на языке  {self.language} ", ],stream=True)
                self.response.resolve()
                self.bot.send_message(message.from_user.id,self.response.text)
                self.bot.register_next_step_handler(message,self.give_recipe)
            except ValueError:
                self.bot.send_message(message.chat.id,"Напишите !рецепт еду и предпочитаемый язык через пробел // Для смены темы напишите stop")
                self.bot.register_next_step_handler(message,self.give_recipe)

    def weather_info(self,message):
        if message.text.lower() == "stop":
                    self.bot.send_message(message.from_user.id,"Вы приостановили функцию,теперь введите /help")
                    try: 
                        self.bot.register_next_step_handler(message,self.get_text_message)

                    except AttributeError:
                         print("")
        else:
            try:
                self.city = message.text
                self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347"
                self.weather_data = requests.get(self.url).json()
                self.weather_round = round(self.weather_data['main']['temp'])
                self.weather_feels = round(self.weather_data["main"]['feels_like'])

                self.result = f"Сейчас в городе {self.city} температура {self.weather_round}, ощущается как {self.weather_feels}"

                self.bot.send_message(message.from_user.id,self.result)
                self.bot.register_next_step_handler(message,self.weather_info)
            except Exception:
                self.bot.send_message(message.from_user.id,"Напишите название города // Для смены темы напишите stop")
                self.bot.register_next_step_handler(message,self.weather_info)

    #* Это чтобы бот мог ответить(Теперь наш бот будет постоянно спрашивать у сервера Телеграмма «Мне кто-нибудь написал?»)'

    def run(self):
        self.bot.infinity_polling()

tele_bot = Tele_bot(api_token)


@app.route('/')
def index():
    return "Telegram bot is running"

@app.route('/webhook',methods=['POST'])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok",200


def setup_bot():
    bot = telebot.TeleBot(api_token)
    bot.remove_webhook()
    bot.set_webhook(url="https://dashboard.render.com/web/new")

if __name__ == "__main__":
    setup_bot()
    app.run(host="0.0.0.0",port=8080)
