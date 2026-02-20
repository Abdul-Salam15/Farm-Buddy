# FarmBuddy 🌾
**Your Intelligent Multi-modal Agricultural Advisor**

FarmBuddy is a state-of-the-art AI platform designed to empower smallholder farmers with real-time, context-aware agricultural guidance. It bridges the literacy and technology gap through multi-modal interaction—voice, text, and vision—delivered via a mobile-first web interface.

---

## ✨ Core Functionalities

### 🗣️ Multi-modal Chat (Voice & Text)
- **Interactive Advice**: Ask questions about crop management, pest control, and planting schedules.
- **Voice Support**: High-quality Text-to-Speech (TTS) and Speech-to-Text (STT) for hands-free operation.
- **Native Languages**: Supports **Hausa**, **Yoruba**, and **Igbo** (plus English) using Meta's MMS (Massively Multilingual Speech) models.
- **Stop Control**: Take control of the audio with the new "Stop" feature to silence the AI during playback.

### 📸 Plant Disease Diagnosis (Vision-AI)
- **Image Analysis**: Upload photos of plant leaves for instant disease detection.
- **Streaming Vision**: Results start appearing word-by-word as the AI analyzes the image, reducing wait times.
- **Actionable Treatment**: Get practical, low-cost solutions tailored for local farming conditions.

### 🌦️ Localized Weather Insights
- **Real-time Data**: Integrated with OpenWeatherMap for current conditions and 5-day forecasts.
- **Contextual Planning**: The AI uses weather data to provide smarter advice (e.g., advising against fertilizer application if heavy rain is expected).

### 📱 Premium UX
- **Lightning Fast**: Optimized context handling and render throttling ensure a "buttery smooth" typing experience.
- **Mobile First**: Responsive glassmorphism design optimized for low-bandwidth 2G/3G connections.
- **Dark Mode**: Eye-friendly interface for low-light environments.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ / Django 5.1+
- **AI Models**: 
  - **Gemini 1.5 Flash**: Multimodal reasoning, planning, and vision analysis.
  - **Meta MMS**: Native language TTS (Hausa/Yoruba).
  - **Edge-TTS**: English & Igbo (Nigerian Accent) speech synthesis.
- **Data Integration**: OpenWeatherMap API
- **Frontend**: Vanilla JS (ES6+), CSS3 (Modern Flex/Grid), HTML5.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **FFmpeg**: Required for audio processing.
  - *Windows*: Download from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
  - *Linux*: `sudo apt install ffmpeg`
  - *Mac*: `brew install ffmpeg`

### Installation

1. **Clone the Repo**
   ```bash
   git clone https://github.com/Abdul-Salam15/Farm-Buddy.git
   cd Farm-Buddy
   ```

2. **Virtual Environment Setup**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_key_here
   OPENWEATHER_API_KEY=your_key_here
   SECRET_KEY=generate_a_random_string
   DEBUG=True
   ALLOWED_HOSTS=*
   ```

5. **Initialize Database**
   ```bash
   python manage.py migrate
   ```

6. **Start FarmBuddy**
   ```bash
   python manage.py runserver
   ```

---

## 💡 Usage Tips

- **First Run**: The Hausa and Yoruba voice models (~150MB each) are downloaded automatically on first use. Ensure you have a stable internet connection for the initial load.
- **Browser TTS**: English responses use your browser's native speech engine for instant playback.
- **Streaming**: You don't need to wait for the "Loading" state to end; text will appear as it arrives!

---

## � License & Author
- **License**: MIT
- **Author**: Abdul-Salam15
- **Contact**: [GitHub Profile](https://github.com/Abdul-Salam15)
