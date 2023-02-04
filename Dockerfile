FROM python:3

WORKDIR /app

COPY . .

RUN python3 -m pip install -U discord.py python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib firebase_admin

CMD python -u ./main.py