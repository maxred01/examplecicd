# Cafe Bot

Telegram-боты и мини-приложение для заказа в кафе.

## Структура

| Файл | Описание |
|------|----------|
| `server.py` | Flask-сервер с API и раздачей мини-приложения |
| `database.py` | SQLite: категории, товары, варианты, заказы |
| `bot_customer.py` | Клиентский Telegram-бот (ссылка на меню) |
| `bot_worker.py` | Бот-работник (приём/отклонение/выполнение заказов) |
| `config.py` | Конфигурация из переменных окружения |
| `run.py` | Запуск всех компонентов |
| `static/miniapp/` | HTML/CSS/JS мини-приложения |

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env` и заполните:

```
CUSTOMER_BOT_TOKEN=...
WORKER_BOT_TOKEN=...
WORKER_CHAT_ID=...
SERVER_URL=https://your-server.com
SECRET_TOKEN=...
```

## Запуск

```bash
python run.py          # всё вместе
python run.py server   # только сервер
python run.py customer # только клиентский бот
python run.py worker   # только бот-работник
```

## Тесты

```bash
cd cafe_bot
python -m pytest tests/ -v
```
