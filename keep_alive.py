import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"  # UptimeRobot이 확인할 응답

def run():
    port = int(os.environ.get("PORT", 8080))  # Render가 제공하는 PORT 환경변수 사용
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
