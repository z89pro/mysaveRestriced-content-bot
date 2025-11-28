from flask import Flask
import logging

app = Flask(__name__)

# Reduce logging clutter
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def hello_world():
    return 'VJ Save Restricted Bot is Running 24/7'

@app.route('/health')
def health_check():
    return 'OK', 200

if __name__ == "__main__":
    app.run()