FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U discord.py python-dotenv

CMD python -u ./main.py