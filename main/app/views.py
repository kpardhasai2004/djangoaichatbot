import requests
from django.shortcuts import render,redirect
from .models import conversations
from gtts import gTTS
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import os



def home(request):
    conversationss = conversations.objects.all().order_by("-created_at")
    return render(request,"index.html",{"conversationss":conversationss})


def chatbot(request):
    if request.method == 'GET':
        # Read the user input
        user_input = request.GET.get("input")

        # Set the API endpoint
        endpoint = "https://api.openai.com/v1/engines/text-davinci-003/completions"

        # Set the API key
        api_key = "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"

        # Set the request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Set the request data
        data = {
            "prompt": user_input,
            "temperature": 0.5,
            "max_tokens": 1024,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        # Make the API request
        response = requests.post(endpoint, headers=headers, json=data)
        response_data = response.json()

        # Extract the response text
        response_text = response_data["choices"][0]["text"]
        # Get the user input from the form
        # Generate audio file using gTTS
        text = response_text
        # Generate the audio file
        audio_bytes = BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        # Save the audio file to disk and to the database
        filename = user_input.replace(' ', '_')
        i = 1
        while os.path.exists("media/"+filename+".mp3"):
            filename = f"{filename}_{i}"
            i += 1
        audio_path = f'media/{filename}.mp3'
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes.getbuffer())
        
        # Save audio file to model instance
        #saving data in the model conversations
        prompt = user_input
        message = response_text
        conv=conversations(prompt=prompt,message=message,audio_path=audio_path)
        conv.save()
        conversationss = conversations.objects.all().order_by("-created_at")
        return redirect("home")

def cdelete(request, id):
    if request.method == 'POST':

        os.remove(conversations.objects.get(id=id).audio_path)
        conversations.objects.get(id=id).delete()
    return redirect('home')






