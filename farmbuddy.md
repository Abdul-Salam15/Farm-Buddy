# AI-Powered Multimodal Agricultural Companion for Smallholder Farmers

## Project Overview

We are building an **AI-powered agricultural companion platform** that allows Nigerian smallholder farmers to interact with the system via:

- 🎤 Voice (STT)
- 🔊 Voice output (TTS)
- 📸 Plant image uploads for disease detection
- 🌦️ Weather forecasts
- 💬 Text chat for agricultural advice

The platform must support **Explainable AI (XAI)** for transparency and trust, providing feature attribution and rationale for recommendations. It will include a **Telegram chatbot** optimized for **2G/3G connectivity**, in addition to a **Streamlit web dashboard** for extension agents.

Key functionality includes:

- Personalized advice based on weather, soil, and crop data
- Crop management recommendations (e.g., when to plant maize)
- Disease diagnosis via image recognition
- Market price forecasting and selling recommendations
- Low-bandwidth mobile accessibility
- Transparent AI explanations (SHAP visualizations)

---

## Phased Learning + Building Roadmap (Streamlit)

The project will be implemented in **phases**, each building on the previous, to handle complexity and context limits in AI planning.

---

### 🔹 PHASE 1: Core Streamlit + Basic Chatbot (FOUNDATION)

**Goal:** Build a simple text-based farming chatbot.

**Key Features:**

- Farmer types a question
- AI responds with agricultural advice
- No voice or image handling yet

**Concepts to Learn:**

- Streamlit basics: `st.text_input`, `st.button`, `st.write`
- Basic Python functions
- Calling an AI API (e.g., ChatGPT, Gemini)
- Simple prompt design

**Chapter Mapping:** 4.2 Chatbot Implementation  
**Outcome:** Working text-based chatbot. Ready to start writing Chapter 4.

---

### 🔹 PHASE 2: Context-Aware Agricultural Chatbot (SMARTER CHAT)

**Goal:** Enhance chatbot with memory and context.

**Key Features:**

- Conversation history retained
- Context-aware responses
- Personalized agricultural advice

**Concepts to Learn:**

- Streamlit session state
- Prompt engineering with context injection
- Conversation-aware NLP

**Chapter Mapping:** Context-aware NLP, Conversational AI  
**Outcome:** Chatbot feels intelligent; academically justifiable as a DSS.

---

### 🔹 PHASE 3: Voice Input & Voice Output (HANDS-FREE USE)

**Goal:** Enable hands-free interaction for farmers.

**Key Features:**

- Speech-to-text input
- Text-to-speech output

**Concepts to Learn:**

- STT and TTS
- Audio handling in Python
- Streamlit file/audio inputs

**Integration:**  
`Voice → Text → Chatbot → Text → Voice`

**Chapter Mapping:** 4.3 Voice Interaction Module, ASR, Speech synthesis  
**Outcome:** Supports illiterate or semi-literate farmers; increases project impact.

---

### 🔹 PHASE 4: Image-Based Plant Disease Detection

**Goal:** Add image-based diagnostic capabilities.

**Key Features:**

- Upload plant leaf images
- Pre-trained CNN predicts disease
- Chatbot explains disease and recommended actions

**Concepts to Learn:**

- Streamlit image upload
- Image preprocessing
- Using pre-trained CNN models (transfer learning)

**Chapter Mapping:** 4.4 Plant Disease Detection, Computer Vision, CNN  
**Outcome:** Multi-modal system; strong visual component for supervisors.

---

### 🔹 PHASE 5: Weather Information Integration

**Goal:** Provide real-time weather advice.

**Key Features:**

- Fetch weather data via API
- Chatbot uses forecasts to guide planting decisions

**Concepts to Learn:**

- API calls
- JSON handling
- Streamlit data display

**Chapter Mapping:** 4.5 Weather Data Integration, API-based DSS  
**Outcome:** Supports real agricultural decisions.

---

### 🔹 PHASE 6: Market Price Information

**Goal:** Add crop pricing and market advisory.

**Key Features:**

- Market price lookup
- Market trend explanation by chatbot

**Concepts to Learn:**

- Data handling (CSV / API)
- Simple analytics
- LLM explanation

**Chapter Mapping:** 4.6 Market Information Module, Data-driven advisory systems  
**Outcome:** Covers production + selling; strong real-world relevance.

---

### 🔹 PHASE 7: Integration & Polishing (FINAL FORM)

**Goal:** Combine all modules into a coherent system.

**Key Features:**

- Sidebar navigation
- Clear UI sections
- Error handling
- Simple documentation

**Outcome:** Complete platform integrating text, voice, images, weather, market, and XAI insights.

---

## Additional Requirements

### 1. Telegram Bot (2G/3G Optimization)

- Must support text and voice chat
- Low-bandwidth responses (<50 KB per query)
- Seamlessly connects with ML modules

### 2. Explainable AI (XAI)

- Use SHAP to visualize feature importance
- Provide textual rationale to farmers
- Integrate explanations in web dashboard

### 3. Machine Learning Modules

- **Random Forest:** Yield prediction
- **LSTM:** Price forecasting
- **CNN:** Plant disease detection
- All models must support inference pipelines and API integration

### 4. Dataset Ingestion

- Ingest open-source datasets for maize and cassava
- Clean and merge datasets into unified format
- Extract features relevant to agronomy and market forecasting

### 5. Evaluation Metrics Logging

- Log performance metrics (F1, RMSE, accuracy)
- Maintain historical model performance
- Use metrics to improve recommendations over time

---

## Notes for the LLM

- Break the build into **modules** to avoid context limits
- Focus on **Streamlit first**, then Telegram bot integration
- Ensure **XAI explanations** are embedded in all advisory outputs
- Each phase builds incrementally; previous phases are foundation for the next
- Include **voice, image, weather, market, and context-aware conversation** in final integration
