from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import subprocess
import signal
import logging

import requests
from bs4 import BeautifulSoup

import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Only show errors, hide 200 logs

app = Flask(__name__)

# Path to files
CONV_FILE = "data/conv.txt"
STATUS_FILE = "data/status.txt"
DATA_FILE = "data/data.txt"
TODOS_FILE = "data/todos.json"
process = None  # global var to track main.py process
scraping_process = None
program_running = False

def update_weather_data():
    url = "https://www.timeanddate.com/weather/republic-of-macedonia/skopje/ext"
    
    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    current_wether_div = soup.select_one("#currentAlert > div")

    if current_wether_div:
        current_wether_text = ""
        for content in current_wether_div.contents:
            if content.name != "span" and content.name != "img" and content.name != "a" and content.name != "div":  # skip span
                if isinstance(content, str):
                    current_wether_text += content.strip()
    
    # Select Forcast data
    forcast_weather_date = soup.select("#wt-ext > tbody > tr > th")
    forcast_weather_overall = soup.select("#wt-ext > tbody > tr > td.small")
    forcast_weather_temp = soup.select("#wt-ext > tbody > tr > td:nth-child(5)")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(f"Current Weather: {current_wether_text}\n")
        f.write("14 Day Forcast Data: \n")
        for date, overall, temp in zip(forcast_weather_date, forcast_weather_overall, forcast_weather_temp):
            f.write(f"{date.get_text()} - {overall.get_text()} - {temp.get_text()} \n")

def update_news_data():
    url = "https://www.techmeme.com/"

    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    headlines = []

    # Get first 10 headlines
    for i in range(1, 11):
        # To get the headlines need to select a tags with following selectors: #\30 i1 > div.ii > strong > a , #\31 i1 > div.ii > strong > a , #\32 i1 > div.ii > strong > a
        selector = f"#\\3{i} i1 > div.ii > strong > a"
        a_tag = soup.select(selector)
        if a_tag:
            headlines.append(a_tag[0].get_text(strip=True))

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write("Top news today: \n")
        for headline in headlines:
            f.write(f"Headline: {headline} .\n")

@app.route("/")
def index():
    # Read conversation
    if os.path.exists(CONV_FILE):
        with open(CONV_FILE, "r") as f:
            conversation = [line.strip() for line in f if line.strip()]
    else:
        conversation = []

    # Set default status to idle
    with open(STATUS_FILE, "w") as f:
        f.write("Idle...")

    # Read status
    status = "Idle"
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = f.read()

    return render_template("index.html", conversation=conversation, status=status, program_running = program_running)


@app.route("/reset")
def reset():
    # Clear conv.txt
    with open(CONV_FILE, "w") as f:
        f.write("")

    with open(TODOS_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
    
    return redirect(url_for("index"))

@app.route("/start")
def start_conversation():
    global process, program_running

    # Update Jarvi data by scraping
    with open(DATA_FILE, "w") as f:
        f.write("")

    # Get Weather Data
    update_weather_data()
    # Get News Data
    update_news_data()

    # Run main.py
    if process is None or process.poll() is not None:
        process = subprocess.Popen(["python", "main.py"])
    program_running = True

    # Reset Conversation
    with open(CONV_FILE, "w") as f:
        f.write("")

    with open(TODOS_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
        
    return redirect(url_for("index"))

@app.route("/end")
def end_conversation():
    global process, program_running
    if process and process.poll() is None:
        process.send_signal(signal.SIGINT) # or process.send_signal(signal.SIGINT)
        process = None

    program_running = False

    # Set default status to idle
    with open(STATUS_FILE, "w") as f:
        f.write("Idle...")

    return redirect(url_for("index"))

@app.route("/get_conversation", methods=["GET", "POST"])
def get_conversation():
    global program_running

    if request.method == "POST":
        data = request.get_json()
        if data and data.get("doneSpeaking"):
            with open(STATUS_FILE, "w") as f:
                f.write("Idle")
        return ("", 204)

    if os.path.exists(CONV_FILE):
        with open(CONV_FILE, "r") as f:
            conversation = [line.strip() for line in f if line.strip()]
    else:
        conversation = []

    status = "Idle"
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = f.read()

    return jsonify({
        "status": status,
        "conversation": conversation
    })

@app.route("/get_tasks")
def get_tasks():
    tasks = []
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, reset it
            tasks = []
            with open(TODOS_FILE, "w", encoding="utf-8") as f:
                f.write("[]")

    return jsonify({
        "tasks": tasks
    })

@app.route("/update_task", methods=["POST"])
def update_task():
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    else:
        tasks = []

    data = request.get_json()
    index = data.get("index")
    done = data.get("done")

    if index is not None and 0 <= index < len(tasks):
        tasks[index]["done"] = done
        
        with open(TODOS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)

    return "", 204

@app.route("/scrape_data")
def scrape_data():
    # Update Jarvis data by scraping
    with open(DATA_FILE, "w") as f:
        f.write("")

    # Get Weather Data
    update_weather_data()
    # Get News Data
    update_news_data()

    return redirect(url_for("index"))

@app.route("/audio/<path:filename>")
def audio(filename):
    return send_from_directory("static/audio", filename)

if __name__ == "__main__":
    app.run(debug=True)
