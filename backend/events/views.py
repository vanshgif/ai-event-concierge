import json
from google import genai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EventRequest
import requests
import os
from dotenv import load_dotenv

def get_venue_image(query):
    try:
        url = "https://api.unsplash.com/photos/random"

        params = {
            "query": query,
            "orientation": "landscape",
            "client_id": "dm-jxzfOMh5lHbFHnSNICzaB8jRM8yuYpnu7NwwxYlg"
        }

        response = requests.get(url, params=params)
        data = response.json()

        return data["urls"]["regular"]

    except:
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"

load_dotenv()  # Load environment variables from .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@api_view(['POST'])
def generate_event(request):

    description = request.data.get("description")

    prompt = f"""
You are an AI event planner.

Return ONLY valid JSON in this format:

{{
"venue_name": "",
"location": "",
"estimated_cost": "",
"why_it_fits": "",
"image_query": ""
}}

image_query should describe the venue visually so an image search can find it.

Example image_query:
"luxury mountain lodge colorado resort exterior"

Event description:
{description}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown formatting if Gemini returns it
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        data = json.loads(text)

    except Exception as e:
        return Response({
            "error": "AI generation failed",
            "details": str(e)
        })

    venue = data.get("venue_name")
    location = data.get("location")
    image_query = data.get("image_query", f"{venue} {location} resort")

    # Generate image based on AI query
    image_url = get_venue_image(image_query)

    EventRequest.objects.create(
        user_input=description,
        venue_name=venue,
        location=location,
        estimated_cost=data.get("estimated_cost"),
        why_it_fits=data.get("why_it_fits")
    )

    data["image_url"] = image_url

    return Response(data)


@api_view(['GET'])
def get_history(request):

    events = EventRequest.objects.all().order_by('-created_at')

    data = []

    for e in events:
        data.append({
            "venue_name": e.venue_name,
            "location": e.location,
            "estimated_cost": e.estimated_cost,
            "why_it_fits": e.why_it_fits
        })

    return Response(data)