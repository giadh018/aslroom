from django.http import JsonResponse
from django.shortcuts import render
import cv2
import numpy as np
from .recognize import recognize_sign_language, text_to_speech

def index(request):
    return render(request, 'base/index.html')

def lobby(request):
    return render(request, 'base/lobby.html')

def room(request):
    return render(request, 'base/room.html')

def recognize(request):
    if request.method == 'POST':
        try:
            frame = request.FILES['frame']
            img = cv2.imdecode(np.frombuffer(frame.read(), np.uint8), cv2.IMREAD_COLOR)
            character, imgOutput, x, y, w, h, label = recognize_sign_language(img)
            return JsonResponse({'character': character, 'label': label})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def speak(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        text_to_speech(text)
        return JsonResponse({'status': 'success'})