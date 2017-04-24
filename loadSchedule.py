from ParserXLSX import parse
from const import HUD
from keys import PATH_TO_FILES

def load_schedule(message, bot, db):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        ext = file_info.file_path.split(".")[1]
        if(ext=="xlsx") or (ext == "xls"):
            downloaded_file = bot.download_file(file_info.file_path)
            src = PATH_TO_FILES + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
                parsing = parse(db, src)
                if(parsing != True):
                    bot.send_message(message.chat.id, HUD.LOADFILE_ERROR)
                    for i in parsing:
                        bot.send_message(message.chat.id, "Столбец: %d, Строка: %d" % (i["error_row"], i["error_col"]));
                else:
                    bot.send_message(message.chat.id, HUD.LOADFILE_SUCCESS)

    except Exception as e:
        bot.send_message(message.chat.id, HUD.LOADFILE_ERROR)