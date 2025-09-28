# Jarvis - AI Voice Assistant (Demo)

An interactive AI-powered assistant with a modern web interface, built using Flask, JavaScript, and Python.
This demo web design project was built with **Flask**, showcasing responsive layouts, modern styling, and clean code structure.  
This project was created as a portfolio piece to demonstrate both back-end and front-end integration for small web apps.

---

## 🚀 Features
- Natural conversation with Jarvis (chat + audio response)
- Dynamic task manager (add, mark complete, delete)
- Web Scraping for news and weather information
- Real-time audio visualizer
- Modern responsive UI with custom CSS animations

## 🚀 Features

- 🎨 Responsive design with HTML5, CSS3, and JavaScript
- ⚡ Flask back-end for dynamic content
- 📂 Organized project structure (`static/` & `templates/`)
- 🖼️ Easy theming and customization
- 🛠️ Ready to deploy on platforms like Render, Vercel, or Heroku

---

## 🛠 Tech Stack
- **Backend:** Flask, Python
- **Frontend:** HTML, CSS, JavaScript
- **Audio:** PyAudio, Pygame
- **AI Integration:** ElevenLabs, Deepgram, Google GenAI

---

## 📂 Project Structure

```
Jarvis-WebDesignProject/
│── app.py              # Flask application entry point
│── main.py             # Jarvis AI logic
│── storage.py          # Task storage
│── record.py           # Function for recording audio from a microphone.
│── requirements.txt    # Python dependencies
│── .gitignore          # Ignore unnecessary files
│── README.md           # Project documentation
│
├── static/             # CSS, images
│   ├── css/
│   └── images/
│
├── templates/          # HTML templates and JS
│   └── index.html
│
└── docs/ 
```

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Skittzy/Jarvis-AIPersonalAssistant.git
   cd Jarvis-AIPersonalAssistant
   ```

2. **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate    # On Mac/Linux
    venv\Scripts\activate       # On Windows
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **ADD YOUR API KEYS IN .env FILE!:**
    ```bash
    DEEPGRAM_API_KEY=YOUR_KEY_HERE
    ELEVENLABS_API_KEY=YOUR_KEY_HERE
    GOOGLE_API_KEY=YOUR_KEY_HERE
    ```

5. **Run the project:**
    ```bash
    python app.py
    ```
    The app will be available at:  
    👉 http://127.0.0.1:5000/

---

## 🎥 Demo

![Demo Showcase](docs/JarvisAIPersonalAssistentShowcase.gif)  

---

## 📦 Deployment

This project can be deployed on free hosting platforms:  

- [Heroku](https://www.heroku.com/)  
- [Render](https://render.com/)  
- [Vercel](https://vercel.com/) (with Flask adapter)  

---

## 🤝 Contributing

This is a personal portfolio demo, but feel free to fork and adapt the project for your own use.  
Pull requests are welcome if you’d like to suggest improvements.

---

## 📜 License

This project is licensed under the **GPL v3.0 License** – see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

Created by [Matej Krsteski](https://skittzy.github.io/personal-portfolio/).  
If you like this project, give it a ⭐ on GitHub!