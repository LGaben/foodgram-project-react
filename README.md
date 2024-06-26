# Foodgram
### Описание
«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Как запустить проект на сервере:

Установить на сервере docker и docker-compose. Скопировать на сервер файлы docker-compose.yaml и default.conf:

```
scp docker-compose.yml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yml
scp nginx.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf

```

Добавить в Secrets на Github следующие данные:

```
DOCKER_PASSWORD # Пароль от аккаунта на DockerHub
DOCKER_USERNAME # Username в аккаунте на DockerHub
HOST # IP удалённого сервера
USER # Логин на удалённом сервере
SSH_KEY # SSH-key компьютера, с которого будет происходить подключение к удалённому серверу
SSH_PASSPHRASE #Если для ssh используется фраза-пароль
TELEGRAM_TO #ID пользователя в Telegram
TELEGRAM_TOKEN #токен бота в Telegram

Выполнить команды:

*   git add .
*   git commit -m "*комментарий*"
*   git push

Далее будут запущены процессы workflow:
*   сборка и доставка докер-образа для контейнера web на Docker Hub
*   автоматический деплой проекта на боевой сервер
*   отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

Далее нужно создать супер пользователя

```sudo docker-compose exec web python manage.py createsuperuser```


### Автор проекта

**Филин Иван.**
