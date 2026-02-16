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
        
        # Get conversation history for context
        messages_history = list(conversation.messages.all().values('role', 'content'))
        
        # Get AI response
        try:
            weather_context = request.session.get('weather_context')
            ai_response = ask_gemini(messages_history, weather_context=weather_context)
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            ai_response = "I'm sorry, I'm having trouble connecting right now. Please try again."
        
        # Save AI response
        Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_response
        )
        
        # Update conversation title if it's the first message
        if conversation.messages.count() == 2:  # user + assistant
            try:
                from utils.gemini_api import summarize_title
                conversation.title = summarize_title(user_message)
            except Exception:
                # Fallback
                conversation.title = user_message[:30] + '...'
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
        
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
