install:
		pip install poetry && \
		poetry install

start:
		poetry run python Telegram_bot/main.py