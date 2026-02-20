from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gemini_api import ask_gemini
from utils.weather_api import get_weather, get_forecast, format_weather_for_ai, format_forecast_for_ai

from .models import Conversation, Message


def index(request, conversation_id=None):
    """Main chat interface"""
    # If specific conversation requested via URL
    if conversation_id:
        try:
            current_conversation = Conversation.objects.get(id=conversation_id)
            request.session['conversation_id'] = current_conversation.id
        except Conversation.DoesNotExist:
            return redirect('index')
    else:
        # Get or create current conversation from session
        session_conv_id = request.session.get('conversation_id')
        if session_conv_id:
            try:
                current_conversation = Conversation.objects.get(id=session_conv_id)
            except Conversation.DoesNotExist:
                # Fallback to latest conversation
                latest = Conversation.objects.order_by('-updated_at').first()
                if latest:
                    current_conversation = latest
                else:
                    current_conversation = Conversation.objects.create()
                request.session['conversation_id'] = current_conversation.id
        else:
            # Try to get latest conversation
            latest = Conversation.objects.order_by('-updated_at').first()
            if latest:
                current_conversation = latest
            else:
                current_conversation = Conversation.objects.create()
            request.session['conversation_id'] = current_conversation.id
    
    # Get messages for current conversation
    messages = current_conversation.messages.all()
    
    # Get all conversations for sidebar (ordered by updated_at)
    conversations = Conversation.objects.all().order_by('-updated_at')[:20]
    
    context = {
        'current_conversation': current_conversation,
        'messages': messages,
        'conversations': conversations,
    }
    
    return render(request, 'chat/index.html', context)


@require_http_methods(["POST"])
def send_message(request):
    """Handle sending a message and getting AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Empty message'})
        
        # Get current conversation
        conversation_id = request.session.get('conversation_id')
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Save user message
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        from django.http import StreamingHttpResponse

        # Get conversation history for context
        messages_history = list(conversation.messages.all().values('role', 'content'))
        
        # Generator for streaming response
        def response_generator():
            full_response = ""
            try:
                weather_context = request.session.get('weather_context')
                # Request streaming from Gemini
                stream = ask_gemini(messages_history, weather_context=weather_context, stream=True, language=language)
                
                for chunk in stream:
                    full_response += chunk
                    # Yield chunk as JSON line (NDJSON style or simple data)
                    yield json.dumps({'chunk': chunk}) + "\n"
                
                # Save full response to DB after streaming is complete
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=full_response
                )
                
                # Signal completion
                yield json.dumps({'success': True, 'full_text': full_response}) + "\n"
                
                # Update title in background if needed (logic moved here to run after response)
                if conversation.messages.count() == 2:
                     def update_title_background(conv_id, text):
                        try:
                            from utils.gemini_api import summarize_title
                            c = Conversation.objects.get(id=conv_id)
                            c.title = summarize_title(text)
                            c.save()
                        except Exception as e:
                            print(f"Error updating title: {e}")

                     import threading
                     thread = threading.Thread(target=update_title_background, args=(conversation.id, user_message))
                     thread.daemon = True
                     thread.start()

            except Exception as e:
                print(f"Stream Error: {e}")
                yield json.dumps({'error': str(e)}) + "\n"

        return StreamingHttpResponse(response_generator(), content_type='application/x-ndjson')
        
    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def new_conversation(request):
    """Create a new conversation"""
    try:
        conversation = Conversation.objects.create()
        request.session['conversation_id'] = conversation.id
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def upload_image(request):
    """Handle plant image upload and analysis"""
    try:
        from utils.gemini_api import analyze_plant_image
        from utils.image_processing import validate_image
        from django.core.files.storage import default_storage
        
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Validate image
        is_valid, error_msg = validate_image(image_file)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        
        # Get current conversation
        conversation_id = request.session.get('conversation_id')
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Get optional text caption
        text_content = request.POST.get('message', '').strip()
        if not text_content:
            text_content = '[Plant image uploaded for analysis]'
            
        # Save user message with image
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=text_content,
            image=image_file
        )
        
        # Get the saved image path
        image_path = user_message.image.path
        
        from django.http import StreamingHttpResponse

        # Save AI response placeholder and then yield chunks
        def vision_response_generator():
            full_response = ""
            try:
                # Analyze image with Gemini Vision in streaming mode
                stream = analyze_plant_image(image_path, stream=True)
                
                for chunk in stream:
                    full_response += chunk
                    yield json.dumps({'chunk': chunk}) + "\n"
                
                # Save AI response to DB
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=full_response
                )
                
                # Signal completion
                yield json.dumps({'success': True, 'full_text': full_response, 'image_url': user_message.image.url}) + "\n"
                
                if conversation.messages.count() == 2:
                    conversation.title = "Plant Disease Analysis"
                    conversation.save()

            except Exception as e:
                print(f"Error in vision stream: {e}")
                yield json.dumps({'success': False, 'error': str(e)}) + "\n"

        return StreamingHttpResponse(vision_response_generator(), content_type='application/x-ndjson')
        
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def rename_conversation(request, conversation_id):
    """Rename a conversation"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        data = json.loads(request.body)
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return JsonResponse({'success': False, 'error': 'Empty title'}, status=400)
            
        conversation.title = new_title[:200]
        conversation.save()
        
        return JsonResponse({'success': True, 'title': conversation.title})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST", "DELETE"])  # Allow POST for simplicity if DELETE tricky
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        conversation.delete()
        
        # If deleted current conversation, clear session
        if str(request.session.get('conversation_id')) == str(conversation_id):
            if 'conversation_id' in request.session:
                del request.session['conversation_id']
                
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["POST"])
def get_weather_data(request):
    """Fetch and store weather data"""
    try:
        data = json.loads(request.body)
        lat = data.get('lat')
        lon = data.get('lon')
        
        if not lat or not lon:
            return JsonResponse({'success': False, 'error': 'Missing coordinates'}, status=400)
            
        weather_data = get_weather(lat, lon)
        forecast_data = get_forecast(lat, lon)
        
        current_report = format_weather_for_ai(weather_data)
        forecast_report = format_forecast_for_ai(forecast_data)
        
        full_report = f"{current_report}\n\n{forecast_report}"
        
        # Store in session for use in next chat message
        request.session['weather_context'] = full_report
        
        return JsonResponse({
            'success': True, 
            'report': full_report,
            'data': {'current': weather_data, 'forecast': forecast_data}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def transcribe_audio(request):
    """Transcribe audio using Gemini"""
    try:
        from utils.gemini_api import analyze_plant_image # Reuse analyzing logic structure
        import google.generativeai as genai
        
        if 'audio' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No audio provided'}, status=400)
            
        audio_file = request.FILES['audio']
        language = request.POST.get('language', 'en')
        
        # Save temp file
        temp_path = f"temp_{audio_file.name}"
        with open(temp_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
                
        try:
            # Upload to Gemini
            myfile = genai.upload_file(temp_path)
            model = genai.GenerativeModel("gemini-flash-lite-latest")
            
            prompt = f"Transcribe this audio exactly as spoken. The language is likely {language} (Hausa/Igbo/Yoruba/English). Return ONLY the transcription text, no other commentary."
            
            result = model.generate_content([myfile, prompt])
            transcription = result.text.strip()
            
            # Cleanup
            os.remove(temp_path)
            
            return JsonResponse({'success': True, 'text': transcription})
            
        except Exception as ignored:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise ignored

    except Exception as e:
        try:
            print(f"Streaming Error: {e}")
        except:
            pass
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Global cache for MMS models
mms_models = {}

def load_mms_model(lang_code):
    """Load and cache MMS model for a given language code"""
    if lang_code in mms_models:
        return mms_models[lang_code]
    
    # Map app codes to MMS codes
    # yo -> yor, ig -> ibo, ha -> hau
    iso_codes = {
        'ha': 'hau',
        'ig': 'ibo',
        'yo': 'yor'
    }
    mms_code = iso_codes.get(lang_code, lang_code)
    
    model_id = f"facebook/mms-tts-{mms_code}"
    try:
        from transformers import VitsModel, AutoTokenizer
        print(f"Loading MMS Model: {model_id}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = VitsModel.from_pretrained(model_id)
        mms_models[lang_code] = (tokenizer, model)
        return tokenizer, model
    except Exception as e:
        print(f"Error loading MMS model {model_id}: {e}")
        return None, None

@require_http_methods(["POST"])
def speak_text(request):
    """Convert text to speech using MMS (Native) + Edge-TTS (English)"""
    try:
        from django.http import HttpResponse
        import io
        import torch
        import scipy.io.wavfile as wav
        import numpy as np
        
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return JsonResponse({'success': False, 'error': 'No text provided'}, status=400)
        
        # Clean text
        clean_text = text.replace('*', '').replace('#', '')
        
        audio_fp = io.BytesIO()
        content_type = 'audio/wav' # Default for MMS

        # Strategy Selection
        if language in ['ha', 'yo']:
            # Use Meta MMS (Native Quality)
            tokenizer, model = load_mms_model(language)
            
            if tokenizer and model:
                inputs = tokenizer(clean_text, return_tensors="pt")
                with torch.no_grad():
                    output = model(**inputs).waveform
                
                # Convert to wav
                output_np = output.numpy().squeeze()
                
                # Write to BytesIO
                wav.write(audio_fp, model.config.sampling_rate, output_np)
                audio_fp.seek(0)
            else:
                 return JsonResponse({'success': False, 'error': f'Failed to load model for {language}'}, status=500)
        
        else:
            # Igbo or English -> edge-tts (Nigerian English Accent)
            import asyncio
            import edge_tts
            
            content_type = 'audio/mpeg'
            # Use Ezinne for Igbo specifically, Abeo for others
            voice = "en-NG-EzinneNeural" if language == 'ig' else "en-NG-AbeoNeural"
            
            async def get_edge_audio():
                communicate = edge_tts.Communicate(clean_text, voice)
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_fp.write(chunk["data"])

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(get_edge_audio())
                loop.close()
            except Exception as e:
                print(f"EdgeTTS Error: {e}")
                # Fallback to gTTS if edge-tts fails
                from gtts import gTTS
                tts = gTTS(text=clean_text, lang='en', slow=False)
                audio_fp = io.BytesIO() # Reset
                tts.write_to_fp(audio_fp)
                content_type = 'audio/mpeg'

            audio_fp.seek(0)
        
        response = HttpResponse(audio_fp.read(), content_type=content_type)
        ext = 'wav' if content_type == 'audio/wav' else 'mp3'
        response['Content-Disposition'] = f'inline; filename="response.{ext}"'
        return response
        
    except Exception as e:
        try:
            print(f"TTS Error: {e}")
        except:
            pass
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
