import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import sqlite3

# Авторизация бота
vk_session = vk_api.VkApi(token='твой вк токен')
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 'токен группы')

photo_url1 = 'https://imgur.com/a/tEnEHmP'  # мои фильмы
photo_url2 = 'https://imgur.com/a/LRjrPca'  # админ запрос
photo_url3 = 'https://imgur.com/a/eqdAia3'  # добавить фильм

keyboard = {
    "one_time": False,
    "buttons": [
        [
            {"action": {"type": "text", "label": "Добавить фильм"}, "color": "primary"},
            {"action": {"type": "text", "label": "Мои фильмы"}, "color": "primary"},
            {"action": {"type": "text", "label": "Все фильмы пользователей"}, "color": "primary"},
            {"action": {"type": "text", "label": "Анкета на админа"}, "color": "primary"}
        ]
    ]
}

# Обработчик команды /start
def start_message(user_id):
    vk.messages.send(user_id=user_id, message='Привет! Я бот для работы с базой данных. Напиши привет или используй кнопки',
                     keyboard=keyboard)

# Обработчик текстовых сообщений для добавления фильма
def add_film_step(user_id, message_text):
    conn = sqlite3.connect('BDforPython.db')
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS films (_id INTEGER PRIMARY KEY, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS userfilms (user_id INTEGER, films_id INTEGER)")
    
    # Создаем таблицу usersteps, если она не существует
    cursor.execute("CREATE TABLE IF NOT EXISTS usersteps (user_id INTEGER PRIMARY KEY, step INTEGER, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    
    # Проверяем на каком этапе добавления фильма находится пользователь
    cursor.execute("SELECT * FROM usersteps WHERE user_id=?", (user_id,))
    user_step = cursor.fetchone()

# Основной цикл обработки сообщений
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        message_text = event.obj.message['text']
        
        if message_text.lower() == 'привет':
            vk.messages.send(user_id=user_id, message='привет!))')
        elif message_text.lower() == 'пока':
            vk.messages.send(user_id=user_id, message='покеда!')
        else:
            add_film_step(user_id, message_text)
# Обработчик текстовых сообщений для добавления фильма
def add_film_step(user_id, message_text):
    conn = sqlite3.connect('BDforPython.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS films (_id INTEGER PRIMARY KEY, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS userfilms (user_id INTEGER, films_id INTEGER)")
    
    # Создаем таблицу usersteps, если она не существует
    cursor.execute("CREATE TABLE IF NOT EXISTS usersteps (user_id INTEGER PRIMARY KEY, step INTEGER, title TEXT, year INTEGER, type TEXT, director TEXT, achievement TEXT)")
    
    # Проверяем на каком этапе добавления фильма находится пользователь
    cursor.execute("SELECT * FROM usersteps WHERE user_id=?", (user_id,))
    user_step = cursor.fetchone()
    
    if not user_step:
        # Если пользователь еще не начал добавление фильма, начинаем с первого шага
        cursor.execute("INSERT INTO usersteps (user_id, step) VALUES (?, ?)", (user_id, 1))
        conn.commit()
    else:
        step = user_step[1]
        if step == 1:
            # Добавляем название фильма
            cursor.execute("UPDATE usersteps SET step=2, title=? WHERE user_id=?", (message_text, user_id))
            conn.commit()
            vk.messages.send(user_id=user_id, message="Введите год выпуска фильма:")
        elif step == 2:
            # Добавляем год выпуска фильма
            cursor.execute("UPDATE usersteps SET step=3, year=? WHERE user_id=?", (message_text, user_id))
            conn.commit()
            vk.messages.send(user_id=user_id, message="Введите тип фильма (художественный или документальный):")
        elif step == 3:
            # Добавляем тип фильма
            cursor.execute("UPDATE usersteps SET step=4, type=? WHERE user_id=?", (message_text, user_id))
            conn.commit()
            vk.messages.send(user_id=user_id, message="Введите автора фильма:")
        elif step == 4:
            # Добавляем автора фильма
            cursor.execute("UPDATE usersteps SET step=5, director=? WHERE user_id=?", (message_text, user_id))
            conn.commit()
            vk.messages.send(user_id=user_id, message="Введите награду фильма:")
        elif step == 5:
            # Добавляем награду фильма и завершаем добавление
            cursor.execute("INSERT INTO films (title, year, type, director, achievement) VALUES (?, ?, ?, ?, ?)",
                           (user_step[2], user_step[3], user_step[4], user_step[5], message_text))
            conn.commit()
            
            # Добавляем запись о том, что пользователь добавил этот фильм
            film_id = cursor.lastrowid
            cursor.execute("INSERT INTO userfilms (user_id, films_id) VALUES (?, ?)", (user_id, film_id))
            conn.commit()
            
            vk.messages.send(user_id=user_id, message=f"Фильм {user_step[2]} успешно добавлен в базу данных!")
            
            # Сбрасываем шаг пользователя
            cursor.execute("DELETE FROM usersteps WHERE user_id=?", (user_id,))
            conn.commit()
    
    cursor.close()
    conn.close()

# Основной цикл обработки сообщений
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        message_text = event.obj.message['text']
        
        add_film_step(user_id, message_text)
# Обработчик инлайн-кнопок
def handle_callback(event):
    if event.data == 'add_films':
        vk.messages.send(user_id=event.user_id, message="Начнем добавление фильма. Введите название дважды:")
    elif event.data == 'show_user_films':
        conn = sqlite3.connect('BDforPython.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT title FROM films WHERE _id IN (SELECT films_id FROM userfilms WHERE user_id=?)", (event.user_id,))
        user_films = cursor.fetchall()
        
        if user_films:
            films_list = "\n".join([film[0] for film in user_films])
            vk.messages.send(user_id=event.user_id, message=f"Ваши фильмы:\n{films_list}")
        else:
            vk.messages.send(user_id=event.user_id, message="У вас пока нет добавленных фильмов.")
        
        cursor.close()
        conn.close()
    # Другие обработчики кнопок здесь

# Основной цикл обработки сообщений
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.obj.message['from_id']
        message_text = event.obj.message['text']
        
        if message_text.startswith('/start'):
            # Обработка команды /start
            # Отправка клавиатуры с кнопками
            keyboard = {
                "one_time": False,
                "buttons": [
                    [{
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"1\"}",
                            "label": "Добавить фильм"
                        },
                        "color": "primary"
                    }],
                    [{
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"2\"}",
                            "label": "Мои фильмы"
                        },
                        "color": "primary"
                    }],
                    # Другие кнопки
                ]
            }
            vk.messages.send(user_id=user_id, message="Выберите действие:", keyboard=keyboard)
        elif message_text.startswith('/callback'):
            # Обработка инлайн-кнопок
            handle_callback(event)