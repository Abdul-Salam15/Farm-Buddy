import os
import logging
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from utils.gemini_api import ask_gemini, analyze_plant_image
from telegram.request import HTTPXRequest
from functools import partial
from utils.weather_api import get_weather, get_forecast, get_weather_by_city, get_forecast_by_city

# ... (logging config remains same)

class Command(BaseCommand):
    help = 'Runs the Telegram Bot'
    
    # Enhanced in-memory session storage
    user_sessions = {}

    def handle(self, *args, **options):
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN not found in .env'))
            return

        request = HTTPXRequest(connect_timeout=60, read_timeout=60, write_timeout=60, pool_timeout=60)
        application = ApplicationBuilder().token(telegram_token).request(request).build()

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('clear', self.clear_history))
        application.add_handler(CommandHandler('forecast5', self.forecast5))
        application.add_handler(CommandHandler('forecast', self.current_weather))
        
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))

        self.stdout.write(self.style.SUCCESS('Starting Telegram Bot...'))
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Hello! I am FarmBuddy 🌾.\n"
                "I can help you with agricultural advice.\n\n"
                "📍 **Features:**\n"
                "- **Send Location**: Updates weather context for advice.\n"
                "- **/forecast [city]**: Current weather (e.g., `/forecast Ikeja`).\n"
                "- **/forecast5 [city]**: 5-day forecast.\n"
                "- **Send Photo**: Analyze plants for diseases.\n"
                "- **/clear**: Start a new conversation.\n"
                "- **Voice/Text**: Ask me anything!"
            ),
            parse_mode='Markdown'
        )

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if chat_id in self.user_sessions:
            self.user_sessions[chat_id]['history'] = []
        # Always confirm clearing
        await context.bot.send_message(chat_id, "🧹 Conversation history cleared.")

    async def current_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        args = context.args
        loop = asyncio.get_running_loop()
        
        weather_data = None
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        if args:
            city_name = " ".join(args)
            weather_data = await loop.run_in_executor(None, get_weather_by_city, city_name)
        else:
            session = self.user_sessions.get(chat_id, {})
            lat = session.get('lat')
            lon = session.get('lon')
            if lat and lon:
                weather_data = await loop.run_in_executor(None, get_weather, lat, lon)
            else:
                await context.bot.send_message(chat_id, "⚠️ Please send your location first or specify a city (e.g., `/forecast Ikeja`).")
                return

        if weather_data and 'error' not in weather_data:
            city = weather_data['name']
            desc = weather_data['weather'][0]['description'].capitalize()
            temp = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind = weather_data['wind']['speed']
            
            msg = (f"**Current Weather in {city}** 🌡️\n"
                   f"- Condition: {desc}\n"
                   f"- Temp: {temp}°C\n"
                   f"- Humidity: {humidity}%\n"
                   f"- Wind: {wind} m/s")
            await context.bot.send_message(chat_id, msg.replace("**", "*"), parse_mode='Markdown')
        else:
            err = weather_data.get('error', 'Unknown error') if weather_data else "Unknown error"
            await context.bot.send_message(chat_id, f"Could not get weather: {err}")

    async def forecast5(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        args = context.args
        loop = asyncio.get_running_loop()
        
        forecast_data = None
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        if args:
            city_name = " ".join(args)
            forecast_data = await loop.run_in_executor(None, get_forecast_by_city, city_name)
        else:
            session = self.user_sessions.get(chat_id, {})
            lat = session.get('lat')
            lon = session.get('lon')
            if lat and lon:
                forecast_data = await loop.run_in_executor(None, get_forecast, lat, lon)
            else:
                await context.bot.send_message(chat_id, "⚠️ Please send your location first or specify a city (e.g., `/forecast5 Ikeja`).")
                # Set flag to auto-send forecast when location is received
                if chat_id not in self.user_sessions: self.user_sessions[chat_id] = {}
                self.user_sessions[chat_id]['awaiting_forecast'] = True
                return
        
        if forecast_data and 'list' in forecast_data:
            await self.send_forecast_message(context, chat_id, forecast_data)
        else:
            err = forecast_data.get('error', 'Unknown error') if forecast_data else "Unknown error"
            await context.bot.send_message(chat_id, f"Could not retrieve forecast: {err}")
            
    async def send_forecast_message(self, context, chat_id, forecast_data):
        city_name = forecast_data.get('city', {}).get('name', 'Unknown')
        msg = f"**5-Day Forecast for {city_name}** 🌦️\n\n"
        
        daily_forecasts = {}
        for item in forecast_data['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = item
                
        for date, item in list(daily_forecasts.items())[:5]:
            temp = item['main']['temp']
            desc = item['weather'][0]['description']
            msg += f"📅 *{date}*: {desc.capitalize()}, {temp:.1f}°C\n"
        
        msg += "\n*Ask me for advice based on this forecast!*"
        await context.bot.send_message(chat_id, msg.replace("**", "*"), parse_mode='Markdown')

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        photo = update.message.photo[-1] # Get highest resolution
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        try:
            file = await context.bot.get_file(photo.file_id)
            file_path = f"photo_{chat_id}_{photo.file_unique_id}.jpg"
            await file.download_to_drive(file_path)
            
            await context.bot.send_message(chat_id, "🔍 Analyzing image...")
            
            # Check for history
            history = self.user_sessions.get(chat_id, {}).get('history', [])
            
            # Run blocking task in executor
            loop = asyncio.get_running_loop()
            
            # Since analyze_plant_image expects a file path, we can use it directly
            # Note: analyze_plant_image might need minor update if it doesn't handle conversation_history format perfectly
            # But based on Utils, it takes (image_path, conversation_history)
            
            response = await loop.run_in_executor(None, partial(analyze_plant_image, file_path, conversation_history=None))
            
            # Add to history (Multimodal history is tricky in simple list, just add text summary for now)
            history.append({'role': 'user', 'content': '[Sent a photo for analysis]'})
            history.append({'role': 'assistant', 'content': response})
            if chat_id not in self.user_sessions: self.user_sessions[chat_id] = {}
            self.user_sessions[chat_id]['history'] = history
            
            # Format
            # specific fix for Gemini output which uses ** for bold and ### for headers
            formatted_response = response.replace("**", "*").replace("### ", "*").replace("###", "*")
            
            try:
                await context.bot.send_message(chat_id=chat_id, text=formatted_response, parse_mode='Markdown')
            except Exception:
                # Fallback if markdown still fails
                await context.bot.send_message(chat_id=chat_id, text=response)
                
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Error analyzing photo: {str(e)}")
        finally:
            if os.path.exists(file_path): os.remove(file_path)

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        
        # Initialize session if not exists
        if chat_id not in self.user_sessions:
            self.user_sessions[chat_id] = {'history': []}
            
        self.user_sessions[chat_id]['lat'] = lat
        self.user_sessions[chat_id]['lon'] = lon
        
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
                desc = weather_data['weather'][0]['description'].capitalize()
                temp = weather_data['main']['temp']
                humidity = weather_data['main']['humidity']
                wind = weather_data['wind']['speed']
                city = weather_data['name']
                
                context_parts.append(f"Location: {city}. Current Weather: {desc}, {temp}°C, Humidity: {humidity}%, Wind: {wind}m/s.")
                
                msg = (f"✅ **Location set to {city}** 📍\n\n"
                       f"**Current Weather:**\n"
                       f"- Condition: {desc}\n"
                       f"- Temp: {temp}°C\n"
                       f"- Humidity: {humidity}%\n"
                       f"- Wind: {wind} m/s\n\n"
                       f"💡 **Tip:** Type `/forecast5` for a 5-day forecast!")
                
                await context.bot.send_message(chat_id, msg.replace("**", "*"), parse_mode='Markdown')
            else:
                 await context.bot.send_message(chat_id, "⚠️ Could not fetch current weather.")

            # Process forecast for context
            if 'error' not in forecast_data and 'list' in forecast_data:
                # Add a brief summary of forecast to context (e.g., next 3 days rain check)
                rain_likely = any('rain' in x['weather'][0]['main'].lower() for x in forecast_data['list'][:24]) # Check next 3 days (approx 24 points? 3hr intervals -> 8 per day -> 24 items)
                context_parts.append(f"Forecast: {'Rain likely' if rain_likely else 'No rain expected'} in next 3 days.")
                
                # Check for awaiting_forecast flag
                if self.user_sessions.get(chat_id, {}).get('awaiting_forecast'):
                    await self.send_forecast_message(context, chat_id, forecast_data)
                    self.user_sessions[chat_id]['awaiting_forecast'] = False
            
            # Update session context
            if context_parts:
                self.user_sessions[chat_id]['weather_context'] = " ".join(context_parts)
                await context.bot.send_message(chat_id, "I have updated my advice based on your local weather! 🌦️")
            else:
                await context.bot.send_message(chat_id, "⚠️ Weather data unavailable.", parse_mode='Markdown')
            
        except Exception as e:
            await context.bot.send_message(chat_id, f"Error processing location: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        # Initialize session
        if chat_id not in self.user_sessions:
            self.user_sessions[chat_id] = {'history': []}
            
        history = self.user_sessions[chat_id].get('history', [])
        weather_context = self.user_sessions[chat_id].get('weather_context')
        
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')

        try:
            # Append user message to history
            history.append({'role': 'user', 'content': user_text})
            
            # Limit history to last 20 messages to prevent token limits
            if len(history) > 20: history = history[-20:]
            
            # Run blocking task in executor
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, partial(ask_gemini, history, weather_context=weather_context))
            
            # Append assistant response to history
            history.append({'role': 'assistant', 'content': response})
            self.user_sessions[chat_id]['history'] = history
            
            # Format for Telegram Markdown (Legacy)
            formatted_response = response.replace("**", "*").replace("### ", "*").replace("###", "*")
            
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
                
                formatted_response = ai_response.replace("**", "*").replace("### ", "*").replace("###", "*")
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

