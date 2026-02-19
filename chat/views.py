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
        
        # Analyze image with Gemini Vision
        try:
            ai_response = analyze_plant_image(image_path)
        except Exception as e:
            print(f"Gemini Vision API Error: {str(e)}")
            ai_response = "I'm sorry, I'm having trouble analyzing the image right now. Please try again or consult a local agricultural expert."
        
        # Save AI response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # Update conversation title if first message
        if conversation.messages.count() == 2:
            conversation.title = "Plant Disease Analysis"
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'image_url': user_message.image.url
        })
        
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
            model = genai.GenerativeModel("gemini-1.5-flash")
            
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
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def speak_text(request):
    """Convert text to speech using gTTS"""
    try:
        from gtts import gTTS
        from django.http import HttpResponse
        import io
        
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return JsonResponse({'success': False, 'error': 'No text provided'}, status=400)
        
        # Map to gTTS codes (ha, ig, yo are supported)
        # Fallback to English if not supported
        lang_code = language if language in ['en', 'ha', 'ig', 'yo'] else 'en'
        
        # Clean text (remove markdown asterisks etc)
        clean_text = text.replace('*', '').replace('#', '')
        
        # Generate audio
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        
        # Save to memory buffer
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        response = HttpResponse(mp3_fp.read(), content_type='audio/mpeg')
        response['Content-Disposition'] = 'inline; filename="response.mp3"'
        return response
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
