from flask import Flask, render_template, request, jsonify
from discord_webhook import DiscordWebhook
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

conn = sqlite3.connect('messages.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    timestamp TEXT
)
''')
conn.commit()
conn.close()

discord_webhook_url = "https://discord.com/api/webhooks/1439950695951368192/eKQtIlxW4VPDuQu3k2mcbutze37UAP91uObWGQCAAppV5uzPLGqV4TH1W6LRsfkLU1dh"

@app.route("/input_text", methods=['POST'])
def input_text():
    try:
        data = request.get_json(force=True)
        text = data['text']

        send_to_discord(text)
        save_to_database(text)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

def send_to_discord(text):
    webhook = DiscordWebhook(url=discord_webhook_url, content=text)
    webhook.execute()

def save_to_database(text):
    connection = sqlite3.connect('messages.db')
    cur = connection.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute('INSERT INTO messages (content, timestamp) VALUES (?, ?)', (text, timestamp))
    connection.commit()
    connection.close()

@app.route('/get_messages', methods=['GET'])
def get_messages():
    try:
        cutoff_time = datetime.now() - timedelta(hours=30)

        connection = sqlite3.connect('messages.db')
        cur = conn.cursor()

        cur.execute("""
        SELECT content, timestamp FROM messages
         WHERE timestamp >= ?
         """,(cutoff_time.strftime("%Y-%m-%d %H:%M:%S"),))
        messages = cursor.fetchall()

        connection.close()

        return jsonify({'status': 'success', 'messages': messages})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
