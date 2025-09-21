from django.shortcuts import render
from .models import Monastery

def tour_list(request):
    monasteries = Monastery.objects.all()
    return render(request, 'tour.html', {'monasteries': monasteries})


def interactive(request):
    return render(request, 'interactive.html')


def tour(request):
    return render(request, 'tour.html')
  
def index(request):
    return render(request, 'index.html')

import os
import openai
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

openai.api_key = os.getenv("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")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        if not user_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful travel assistant specializing in Sikkim."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            chat_response = response['choices'][0]['message']['content']
            return JsonResponse({"response": chat_response})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)
