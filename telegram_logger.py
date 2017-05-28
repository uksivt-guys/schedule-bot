import logging
import telebot
import keys

bot = telebot.TeleBot(keys.LOGGER_TOKEN)


def send_msg_to_tele_logger(msg):
    bot.send_message(chat_id=keys.LOGGER_GROUP_ID, text=msg)


class TelegramHandler(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            send_msg_to_tele_logger(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)