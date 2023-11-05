FROM python:3.9

WORKDIR /bot

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -U discord.py python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib firebase_admin

CMD python -u ./main.py