FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY settings.py settings.py
RUN pip install -r requirements.txt
CMD [ "/usr/local/bin/python", "-u", "main.py" ]