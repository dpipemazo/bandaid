import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from elevenlabs.client import ElevenLabs


def index_view(request):
    return render(request, "index.html")


@require_http_methods(["POST"])
def text_to_speech_view(request):
    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Text is required."}, status=400)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return JsonResponse({"error": "ElevenLabs API key is not configured."}, status=500)

    client = ElevenLabs(api_key=api_key)

    try:
        audio = client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_multilingual_v2",
            text=text,
            output_format="mp3_44100_128",
        )
    except Exception:
        return JsonResponse({"error": "Failed to generate audio."}, status=500)

    return HttpResponse(audio, content_type="audio/mpeg")
