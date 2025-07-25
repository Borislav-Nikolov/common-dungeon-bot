FROM python:3.12.6

WORKDIR /bot

COPY . .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -U discord.py python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib firebase_admin requests python-socketio websocket-client pillow

CMD python -u ./main.py