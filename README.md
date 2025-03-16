# Бот со списком дней рождений для группового чата
Данный бот работает с базой sqlite в которой хранятся данные:
1) Дата рождения.
2) Имя.
3) Ник телеграм аккаунта.
4) Ссылка на сервис для сбора денег на подарок. Использовать можно любую удобную площадку, либо номер карты.
5) Список поздравлений.

Бот каждый день проверяет в базе когда и у кого будет день рождения, за неделю предупреждает админа в личный чат, о скором празднике. В день рождение отправляет сообщение в общий чат, указывая имя именинника, его ник в телеграм, выбирает рандомное поздравление с базы, которое вы добавили туда заранее и прикрепляет ссылку или номер карты на сбор денег.

Перед запуском внесите ваши данные в файле ```birthdays_bot.py```
```
TOKEN = "<BOT_TOKEN>" # Заменить на ваш токен бота
GROUP_CHAT_ID = <YOUR_CHAT_ID>  # Замените на ваш ID группы
ADMIN_ID = <YOUR_TG_ID>  # Замените на ваш user_id
```
# Список команд бота
/add - Добавить день рождения
Использование: /add Имя @username ДД.ММ.ГГГГ ссылка_на_донат
Пример: /add Ивана @username 16.03.1991 https://example.com

/update_link - Обновить ссылку на донат
Использование: /update_link @username новая_ссылка
Пример: /update_link @username https://newlink.com

/update_name - Обновить имя
Использование: /update_name @username новое_имя
Пример: /update_name @username Ивана

/delete_user - Удалить пользователя
Использование: /delete_user @username
Пример: /delete_user @username

/add_greeting - Добавить поздравление
Использование: /add_greeting текст_поздравления
Пример: /add_greeting С днём рождения, бро! 🎉

/list - Показать список всех пользователей и их дней рождений

# Список поздравлений можно напрямую загрузить через sqlite 
Для массовой загрузки поздравлений выполните в терминале следующее

```
sqlite3 birthdays.db
```

```
INSERT INTO greetings (text) VALUES 
("Бро, с днём рождения! 🎉 Пусть жизнь будет, как крутой трек: с драйвом, скоростью и без пробок! 🚗"),
("С днём рождения, пацан! 🎂 Пусть всё, что ты задумал, сбывается, как по волшебству! ✨"),
("Братан, с днём рождения! 🎉 Пусть удача будет твоим навигатором, а счастье — попутчиком! 🗺️"),
("С днём рождения, кореш! 🎂 Пусть жизнь будет, как крутой сериал: с интересными поворотами и хэппи-эндом! 🎬"),
("Бро, с днём рождения! 🎉 Пусть в твоей жизни будет больше ярких моментов, чем в Instagram! 📸"),
("С днём рождения, пацан! 🎂 Пусть всё, что ты задумал, сбывается, как по щелчку пальцев! ✨"),
("Братан, с днём рождения! 🎉 Пусть жизнь будет, как крутой стрит-арт: яркой и запоминающейся! 🎨"),
("С днём рождения, кореш! 🎂 Пусть в твоей жизни будет больше побед, чем в финале чемпионата! 🏆"),
("Бро, с днём рождения! 🎉 Пусть всё, что ты задумал, сбывается, как по маслу! 🛠️"),
("С днём рождения, пацан! 🎂 Пусть жизнь будет, как крутой фильм: с классным сюжетом и хэппи-эндом! 🎬"),
("Братан, с днём рождения! 🎉 Пусть в твоей жизни будет больше драйва, чем в экшн-игре! 🎮"),
("С днём рождения, кореш! 🎂 Пусть всё, что ты задумал, сбывается, как по волшебству! ✨"),
("Бро, с днём рождения! 🎉 Пусть жизнь будет, как крутой трек: с яркими моментами и без пауз! 🎶"),
("С днём рождения, пацан! 🎂 Пусть удача будет твоей тенью, а проблемы обходят стороной! 🍀"),
("Братан, с днём рождения! 🎉 Пусть в жизни будет больше драйва, чем в гоночном треке! 🏎️"),
("С днём рождения, кореш! 🎂 Пусть всё, что ты задумал, сбывается, как по маслу! 🛠️"),
("Бро, с днём рождения! 🎉 Пусть жизнь будет, как крутой стрит-арт: яркой и запоминающейся! 🎨"),
("С днём рождения, пацан! 🎂 Пусть в твоей жизни будет больше побед, чем в финале чемпионата! 🏆"),
("Братан, с днём рождения! 🎉 Пусть всё, что ты задумал, сбывается, как по щелчку пальцев! ✨"),
("С днём рождения, кореш! 🎂 Пусть жизнь будет, как крутой фильм: с классным сюжетом и хэппи-эндом! 🎬");
```


```
.exit
```

# Пример сообщения в чате

🎉 Сегодня день рождения у Ивана @username! 🎂

С днём рождения, пацан! 🎂 Пусть жизнь будет, как крутой фильм: с классным сюжетом и хэппи-эндом! 🎬

Сбор на подарок тут: https://example.com

# Создание сервиса
Можно настроить автозапуск бота, просто скопируйте unit файл
```
cp ~/birthday_tg_bot/birthday_bot.service /etc/systemd/system/birthday_bot.service
```

```
systemctl daemon-reload
systemctl enable birthday_bot.service
systemctl start birthday_bot.service
```
