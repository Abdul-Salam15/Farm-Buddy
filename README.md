# FarmBuddy 🌾

**AI-Powered Multimodal Agricultural Companion for Smallholder Farmers**

## 📖 Overview

FarmBuddy is an intelligent advisory platform designed to assist smallholder farmers in Nigeria (and beyond) by providing real-time, context-aware agricultural advice. It bridges the gap between complex agricultural data and farmers through accessible interfaces like voice interaction and image analysis.

The system leverages **Google's Gemini AI** for reasoning and **OpenWeatherMap** for localized weather data to offer personalized recommendations.

## ✨ Key Features

*   **🤖 AI Chat Assistant:** Interactive chat for advice on crop management, pest control, and market trends.
*   **🗣️ Voice Interaction:** Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for hands-free operation and accessibility for illiterate users.
*   **📸 Plant Disease Detection:** Analyze plant images to detect diseases and receive treatment recommendations using AI vision.
*   **🌦️ Weather Integration:** Real-time weather updates and 5-day forecasts to inform planting and harvesting decisions.
*   **🌓 Dark Mode:** Eye-friendly optional dark theme for low-light conditions.
*   **📱 Responsive Design:** Optimized for mobile devices and low-bandwidth connections.

## 🛠️ Technology Stack

*   **Backend:** Python, Django
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **AI Engine:** Google Gemini 1.5 Flash (via Generative AI SDK)
*   **Weather Data:** OpenWeatherMap API
*   **Database:** SQLite (Default)
*   **Speech Processing:** Web Speech API (Frontend) / Python SpeechRecognition (Backend fallbacks)

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   Pip
*   Virtualenv (recommended)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Abdul-Salam15/Farm-Buddy.git
    cd Farm-Buddy
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root and add your API keys:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    OPENWEATHER_API_KEY=your_openweather_api_key
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    ```

5.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start the development server:**
    ```bash
    python manage.py runserver
    ```

7.  **Access the app:**
    Open your browser and visit `http://127.0.0.1:8000/chat/`

## 🤝 Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Abdul-Salam15**
*   Email: asalamadebayo@gmail.com
*   GitHub: [Abdul-Salam15](https://github.com/Abdul-Salam15)
