import os
import logging
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from utils.gemini_api import ask_gemini

from telegram.request import HTTPXRequest
from functools import partial

from telegram.request import HTTPXRequest
from functools import partial
from utils.weather_api import get_weather, get_forecast

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class Command(BaseCommand):
    help = 'Runs the Telegram Bot'
    
    # Simple in-memory session storage: {chat_id: {'weather_context': '...'}}
    user_sessions = {}

    def handle(self, *args, **options):
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN not found in .env'))
            return

        # Increase timeouts for 2G/3G networks
        request = HTTPXRequest(
            connect_timeout=60,
            read_timeout=60,
            write_timeout=60,
            pool_timeout=60
        )

        application = ApplicationBuilder().token(telegram_token).request(request).build()

        # Handlers
        start_handler = CommandHandler('start', self.start)
        echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        voice_handler = MessageHandler(filters.VOICE, self.handle_voice)
        location_handler = MessageHandler(filters.LOCATION, self.handle_location)

        application.add_handler(start_handler)
        application.add_handler(echo_handler)
        application.add_handler(voice_handler)
        application.add_handler(location_handler)

        self.stdout.write(self.style.SUCCESS('Starting Telegram Bot...'))
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Hello! I am FarmBuddy 🌾.\n"
                "I can help you with agricultural advice.\n\n"
                "📍 **Tip:** Send me your location so I can give you accurate weather advice!\n"
                "📝 **Usage:** Send text or voice notes."
            ),
            parse_mode='Markdown'
        )

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        try:
            loop = asyncio.get_running_loop()
            
            # Fetch weather and forecast concurrently
            weather_task = loop.run_in_executor(None, get_weather, lat, lon)
            forecast_task = loop.run_in_executor(None, get_forecast, lat, lon)
            
            weather_data, forecast_data = await asyncio.gather(weather_task, forecast_task)
            
            context_parts = []
            
            # Process current weather
            if 'error' not in weather_data:
                desc = weather_data['weather'][0]['description']
                temp = weather_data['main']['temp']
                city = weather_data['name']
                context_parts.append(f"Location: {city}. Current Weather: {desc}, {temp}°C.")
                await context.bot.send_message(chat_id, f"✅ Location set to **{city}**.", parse_mode='Markdown')
            else:
                 await context.bot.send_message(chat_id, "⚠️ Could not fetch current weather.")

            # Process forecast (simplified)
            if 'error' not in forecast_data:
                # Simple summary of tomorrow's forecast logic could go here
                # For now just indicating we have data
                context_parts.append("Forecast data available.")
            
            # Store in session
            if context_parts:
                self.user_sessions[chat_id] = {'weather_context': " ".join(context_parts)}
                await context.bot.send_message(chat_id, "Now I can give you advice based on your local weather! 🌦️")
            
        except Exception as e:
            await context.bot.send_message(chat_id, f"Error processing location: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')

        try:
            # Check for weather context
            weather_context = self.user_sessions.get(chat_id, {}).get('weather_context')
            
            messages = [{'role': 'user', 'content': user_text}]
            
            # Run blocking task in executor
            loop = asyncio.get_running_loop()
            # Pass weather_context to ask_gemini
            response = await loop.run_in_executor(None, partial(ask_gemini, messages, weather_context=weather_context))
            
            # Format for Telegram Markdown (Legacy)
            formatted_response = response.replace("**", "*")
            
            try:
                await context.bot.send_message(chat_id=chat_id, text=formatted_response, parse_mode='Markdown')
            except Exception:
                await context.bot.send_message(chat_id=chat_id, text=response)

        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Sorry, I encountered an error: {str(e)}")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        voice = update.message.voice
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        try:
            file = await context.bot.get_file(voice.file_id)
            file_path = f"voice_{chat_id}_{voice.file_unique_id}.ogg"
            await file.download_to_drive(file_path)
            
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(None, self.process_voice_file, file_path)
            
            if text:
                await context.bot.send_message(chat_id=chat_id, text=f"🎤 You said: \"{text}\"")
                
                # Check for weather context
                weather_context = self.user_sessions.get(chat_id, {}).get('weather_context')
                
                messages = [{'role': 'user', 'content': text}]
                ai_response = await loop.run_in_executor(None, partial(ask_gemini, messages, weather_context=weather_context))
                
                formatted_response = ai_response.replace("**", "*")
                try:
                    await context.bot.send_message(chat_id=chat_id, text=formatted_response, parse_mode='Markdown')
                except Exception:
                    await context.bot.send_message(chat_id=chat_id, text=ai_response)
            else:
                await context.bot.send_message(chat_id=chat_id, text="Sorry, I couldn't understand the audio.")

        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Error processing voice: {str(e)}")
        finally:
            if os.path.exists(file_path): os.remove(file_path)

    def process_voice_file(self, file_path):
        import speech_recognition as sr
        from pydub import AudioSegment
        
        wav_path = file_path.replace(".ogg", ".wav")
        try:
            audio = AudioSegment.from_ogg(file_path)
            audio.export(wav_path, format="wav")
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        except Exception as e:
            logging.error(f"Voice processing error: {e}")
            return None
        finally:
            if os.path.exists(wav_path): os.remove(wav_path)

