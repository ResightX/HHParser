from telebot import TeleBot
from hhparser import scrape
from sqlmanager import manage_data, get_company_data
import time

if __name__ == "__main__":
    token = '' # TOKEN. Используйте Ваш собственный / Use your own
    bot = TeleBot(token)

    @bot.message_handler(commands=['help', 'start'])
    def send_welcome(message):
        bot.reply_to(message, """\
        Команда /parse выведет уведомление об изменениях в базе данных.
    """)

    @bot.message_handler(commands=['parse'])
    def parse(message):
        bot.reply_to(message, 'Ожидайте...')
        print('Scraping in progress. Please wait...')
        data = scrape()
        changeddbdata = manage_data(data[0], data[1])
        newvac = [f'''{nvac.title}    -  Зарплата: {nvac.wage if nvac.wage != 'NULL' else 'Нет данных'}    -   Работодатель:   {nvac.company_name}  -   Рейтинг работодателя: {(get_company_data(nvac.company_name)[0][0]) if get_company_data(nvac.company_name)[0][0] is not None else 'Нет рейтинга'}''' for nvac in changeddbdata[0]]

        if not newvac:
            bot.reply_to(message, "Новых вакансий нет.")
            return

        char_limit = 4000
        current_msg = ""
        msg_count = 1

        print('Done! Check out your telegram bot!')

        for vacancy in newvac:
            if len(current_msg + vacancy + "\n\n") > char_limit:
                bot.reply_to(message, f"Новые вакансии (часть {msg_count}):\n{current_msg}")
                time.sleep(2)
                current_msg = vacancy + "\n\n"
                msg_count += 1
            else:
                current_msg += vacancy + "\n\n"

        if current_msg:
            bot.reply_to(message, f"Новые вакансии (часть {msg_count}):\n{current_msg}")
            time.sleep(2) 

    try:
        bot.infinity_polling()
    except KeyboardInterrupt as ki:
        print(ki)
        exit(0)
