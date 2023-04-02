install:
		virtualenv -p python3 venv; \
		source venv/bin/activate; \
		pip3 install --no-cache -r requirements.txt

start:
		python main.py