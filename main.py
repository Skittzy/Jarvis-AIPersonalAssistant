import os
from os import PathLike
from time import time
import asyncio
from typing import Union
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from deepgram import Deepgram
import pygame
from pygame import mixer
import elevenlabs
from record import speech_to_text

from storage import add_task, mark_done, reset_tasks, load_tasks, load_tasks_as_string
import re

# Load API keys
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

print(f"Loaded GOOGLE_API_KEY: {GOOGLE_API_KEY is not None}")
print(f"Loaded DEEPGRAM_API_KEY: {DEEPGRAM_API_KEY is not None}")
print(f"Loaded ELEVENLABS_API_KEY: {ELEVENLABS_API_KEY is not None}")

# Initialize Google Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize Deepgram client
deepgram = Deepgram(DEEPGRAM_API_KEY)

# Initialize Eleven Labs client
elevenlabs.set_api_key(ELEVENLABS_API_KEY)

# Initialize pygame mixer for audio playback
# mixer.init()

RECORDING_PATH = "static/audio/recording.wav"
DATA_FILE = "data/data.txt"
conversation = []
data_lines = []


def extract_task_from_jarvis_response(response_text: str) -> str:
    # Find the first quoted string in Jarvis's response. So that we get a natural task name.

    match = re.search(r'"(.*?)"', response_text)
    if match:
        return match.group(1)
    return None

# Initial approach: parsing the raw user prompt directly often produced unnatural task names.  
# Example: if the user said, "Jarvis, add a task for me to cook," the stored task name became  
# "a task for me to cook." This made completing tasks awkward, since the user would have to say  
# "mark a task for me to cook done."  
#
# Solution: instead of using the raw prompt, we parse the model’s (Gemini’s) response and extract  
# a clean, quoted task name (e.g., "Cook"). This ensures tasks are natural, concise, and easy to  
# reference when marking them as complete.
def parse_user_prompt(user_prompt: str):
    prompt = user_prompt.lower().strip()

    if ("what can you do" in prompt) or ("help" in prompt):
        return "list_capabilities"  # New intent

    if ("add" in prompt and ("tasks" in prompt or "task" in prompt or "reminders" in prompt or "reminder" in prompt or "remind" in prompt)) or "remind" in prompt:
        return "add_task"

    elif ("mark" in prompt or "update" in prompt) and ("done" in prompt or "complete" in prompt or "finished" in prompt):
        return "mark_done"

    elif ("tasks" in prompt or "reminders" in prompt) and ("reset" in prompt or "clear" in prompt):
        return "reset_tasks"

    elif ("tasks" in prompt or "reminders" in prompt) and ("list" in prompt or "show" in prompt):
        return "list_tasks"

    return None



# Jarvis Personallity settings
JARVIS_INTRO = (
    "You are J.A.R.V.I.S., My AI personal assistant. I like balkan, italian and japanese cuisine, coffe, anime, video games, programming, artificial inteligence and technology."
    "You speak in a calm, precise, and articulate manner with a touch of dry wit. You are unfailingly polite, resourceful, and efficient, often anticipating needs before they are stated. Your humor is subtle and understated, never overshadowing professionalism."
    "You provide concise, intelligent answers and take initiative to assist without excessive questioning."
    'Limit responses to 2–3 short sentences unless further detail is requested. YOUR ANSWERS MUST BE ONE LINE ONLY, DO NOT MAKE NEW LINES. When you are asked to add a task,remeinder you must generate a simple, normal task name incased in " from both sides, if the user says mark them as done, finished you must use the same original name, from previous conversations when you originally added the task, in your reply. '
    "Always address me formally as Sir, but with warmth and occasional light sarcasm."
)

# Request answer from Gemini
def request_gemini(prompt_text: str) -> str:
    current_date_time = datetime.now()

    # Convert conversation list into a single string
    conversation_text = "\n".join(conversation)

    # Convert Data file to string
    global data_lines
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data_lines = [line.strip() for line in f if line.strip()]
    else:
        data_lines = []
    
    data_string = "\n".join(data_lines)

    # Convert todos.json file to string
    tasks_string = load_tasks_as_string()

    # Prompt = Intro Text + Conversation + Real-time Data + todos.json + prompt
    full_prompt = f"{JARVIS_INTRO}\n \nThis is our conversation so far: {conversation_text}\n This is real time data about Today({current_date_time}): {data_string} When asked about the news summirise the most intresting headlines. \n This are my current tasks/remeinders, use this information when the user asks about tasks/remeinders: {tasks_string} \n User prompt: {prompt_text}\n"

    response = client.models.generate_content (
        model="gemini-2.0-flash",
        contents=full_prompt,        
    )
    return response.text


async def transcribe(
    file_name: Union[Union[str, bytes, PathLike[str]], int]
):
    """
    Transcribe audio using Deepgram API.

    Args:
        - file_name: The name of the file to transcribe.

    Returns:
        The response from the API.
    """
    with open(file_name, "rb") as audio:
        source = {"buffer": audio, "mimetype": "audio/wav"}
        response = await deepgram.transcription.prerecorded(source)
        return response["results"]["channels"][0]["alternatives"][0]["words"]


def log(log_msg: str):
    # Print to termnial and write to status.txt
    print(log_msg)
    with open("data/status.txt", "w") as f:
        f.write(log_msg)


if __name__ == "__main__":
    try:
        while True:
            # Record audio
            log("Listening...")
            speech_to_text()
            log("Done listening")

            # Transcribe audio
            current_time = time()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            words = loop.run_until_complete(transcribe(RECORDING_PATH))
            string_words = " ".join(
                word_dict.get("word") for word_dict in words if "word" in word_dict
            )

            # Writes conversation in TEXT FILE
            with open("data/conv.txt", "a") as f:
                f.write(f"User: {string_words}\n")

            conversation.append(f"User: {string_words}") # Update memory

            transcription_time = time() - current_time
            log(f"Finished transcribing in {transcription_time:.2f} seconds.")

            # Get response from Gemini
            current_time = time()

            # Update Tasks/Remeinders if present
            intent = parse_user_prompt(string_words)
            if intent == "list_capabilities":
                response = (
                    "Sir, I can create and manage tasks, list your reminders, provide weather updates, "
                    "share top news, and converse naturally. Though I must admit that I do not have internet access beyond my basic data updates yet."
                )
            else:
                response = request_gemini(string_words)
            response_time = time() - current_time
            log(f"Finished generating response in {response_time:.2f} seconds.")

            task_name = extract_task_from_jarvis_response(response)

            if intent == "add_task":
                if task_name:
                    add_task(task_name)  # Add the natural name from Jarvis
            elif intent == "mark_done":
                if task_name:
                    mark_done(task_name)
            elif intent == "reset_tasks":
                reset_tasks()


            # Convert response to audio
            current_time = time()
            audio = elevenlabs.generate(
                text=response, 
                voice="JBFqnCBsd6RMkjVDRZzb", 
                model="eleven_monolingual_v1"
            )
            elevenlabs.save(audio, "static/audio/response.wav")
            audio_time = time() - current_time
            log(f"Finished generating audio in {audio_time:.2f} seconds.")

            # Play response
            log("Speaking...")
            with open("data/status.txt", "w") as f:
                f.write("Speaking")

            # Add response as a new line to conv.txt
            with open("data/conv.txt", "a") as f:
                f.write(f"Jarvis: {response}\n")

            conversation.append(f"Jarvis: {response}")
            
            # # ------------ Pyaduio player ------------
            # sound = mixer.Sound("audio/response.wav")
            # sound.play()
            # pygame.time.wait(int(sound.get_length() * 1000))

            print(f"\n --- USER: {string_words}\n --- JARVIS: {response}\n")

            #Prevent overlaping
            while True:
                with open("data/status.txt", "r") as f:
                    status = f.read().strip()
                if status != "Speaking":
                    break
    except KeyboardInterrupt:
        print("Jarvis shutting down.")
        # mixer.quit()


