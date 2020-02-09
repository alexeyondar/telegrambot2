FROM python:3.6

RUN pip install python-telegram-bot --upgrade
RUN pip install azure-cosmos --upgrade

COPY /bot.py /bot.py

RUN chmod +x /bot.py

ENTRYPOINT ["/bot.py"]

