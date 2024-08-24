import streamlit as stm
import google.generativeai as genai
import os
import redis
import random
import pandas as pd
import folium
from dotenv import load_dotenv
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import urllib.parse

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
load_dotenv()

redisHost = os.getenv("REDIS_HOST")
redisPort = os.getenv("REDIS_PORT", "6379")
redisPassword = os.getenv("REDIS_PASSWORD")

redisClient = redis.Redis(
    host=redisHost,
    port=int(redisPort),
    password=redisPassword,
    decode_responses=True,
    ssl=True
)


def generateItinerary(prompt):
    """
    Function to generate itinerary with a clean format
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text


def getItinerary(destinationName, typeOfTrip, lengthOfStay, budget):
    """
    Will store the itinerary in Redis for 7 days and check the rate limit of the user
    """
    itineraryKey = getItineraryKey(destinationName, typeOfTrip, lengthOfStay, budget)
    itinerary = getItineraryFromRedis(itineraryKey)

    if itinerary:
        return itinerary

    checkRateLimit()
    prompt = (
        f"Generate a clean and well-formatted {lengthOfStay}-day itinerary for a {typeOfTrip} trip to "
        f"{destinationName} with a budget of {budget}. The itinerary should include activities, places "
        "to visit, and recommendations, but also provide the central coordinates (latitude and longitude) "
        "for the destination city only. The itinerary should be free from special characters like '**', '##', "
        "and formatted for clarity."
    )
    itinerary = generateItinerary(prompt)
    itinerary = formatItinerary(itinerary)
    STORAGE_TIME = 604800  # 7 days in seconds
    redisClient.set(itineraryKey, itinerary, ex=STORAGE_TIME)
    return itinerary


def getItineraryKey(destinationName, typeOfTrip, lengthOfStay, budget):
    """
    Storing the input values to avoid future API calls
    """
    return f"{destinationName}{lengthOfStay}{typeOfTrip}{budget}"


def getItineraryFromRedis(itineraryKey):
    """
    :param itineraryKey:
    :return itinerary if it exists in Redis database:
    """
    if redisClient.exists(itineraryKey):
        itinerary = redisClient.get(itineraryKey)
        if itinerary:
            return itinerary


def checkRateLimit():
    """
    If the request count exceeds the limit, stop the execution
    """
    globalRateLimitKey = "GLOBAL_RATE_LIMIT"
    globalRateLimit = redisClient.get(globalRateLimitKey)

    if globalRateLimit is not None:
        globalRateLimit = int(globalRateLimit)
        requestCount = redisClient.incr("TotalRequestCount")

        if requestCount > globalRateLimit:
            stm.write(
                "You have exceeded the maximum number of requests. Please try again tomorrow."
            )
            stm.stop()


def generatePDF(content):
    """
    Generate a PDF file from the itinerary content.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Draw the content
    c.drawString(72, height - 72, "Travel Itinerary")
    text_object = c.beginText(72, height - 100)
    text_object.setFont("Helvetica", 12)
    for line in content.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def downloadPDF(filename, content):
    buffer = generatePDF(content)
    return stm.download_button(
        label="Download Itinerary as PDF",
        data=buffer,
        file_name=filename,
        mime="application/pdf"
    )


def createMap(coordinates, filename):
    """
    Create and save a map with the given coordinates.
    """
    if not coordinates:
        return
    map_center = coordinates[0]
    m = folium.Map(location=map_center, zoom_start=12)
    for coord in coordinates:
        folium.Marker(location=coord).add_to(m)
    m.save(filename)


def downloadMap(coordinates):
    """
    Generate and provide download link for the map.
    """
    map_filename = "itinerary_map.html"
    createMap(coordinates, map_filename)
    with open(map_filename, "r") as f:
        map_content = f.read()
    return map_filename, map_content


def extractCoordinates(itinerary):
    """
    Extract city center coordinates from the itinerary text.
    """
    coords = []
    # regex to find coordinates in the format of lat, lon
    pattern = re.compile(r"(\d+\.\d+)°\s*[NS],\s*(\d+\.\d+)°\s*[EW]")
    matches = pattern.findall(itinerary)
    for match in matches:
        lat, lon = map(float, match)
        coords.append((lat, lon))
    # print(f"Coordinates are: {coords}")
    return coords


def formatItinerary(itinerary):
    """
    Clean and format the itinerary text
    """
    return itinerary.replace("**", "").replace("##", "").replace(":", "\n")


def shareByEmail(itinerary):
    """
    Create a mailto link for sharing the itinerary via email.
    """
    subject = "Check out my travel itinerary!"
    body = f"Here is my travel itinerary:\n\n{itinerary}"
    mailto_link = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

    stm.markdown(
        f"""
        <a href="{mailto_link}" target="_blank">Share via Email</a>
        """,
        unsafe_allow_html=True
    )

stm.title("Travel Made Easy")
stm.markdown('Get a custom travel plan made just for you!')
destinationName = stm.text_input("Enter your destination")
typeOfTrip = stm.text_input(
    "Enter the type of trip (e.g. Hiking, Solo, Religious, Road, Adventure, Family Vacation, Group Travel etc.)")
lengthOfStay = stm.slider("Enter the length of your stay (days)", 1, 10)
budget = stm.text_input("Enter your budget (e.g. 1000, 5000, etc.)")

with open("loadingMessages.txt", "r") as f:
    loadingMessages = f.readlines()

if stm.button("Recommend"):
    placeholder = stm.empty()
    loadingMessage = random.choice(loadingMessages)

    with stm.spinner(text=loadingMessage):
        itinerary = getItinerary(destinationName, typeOfTrip, lengthOfStay, budget)

    placeholder.text("")
    stm.success(itinerary)

    downloadPDF("itinerary.pdf", itinerary)

    coordinates = extractCoordinates(itinerary)
    if coordinates:
        coords_df = pd.DataFrame(coordinates, columns=["lat", "lon"])
        stm.map(coords_df)

        map_filename, map_content = downloadMap(coordinates)
        stm.download_button(
            label="Download Map",
            data=map_content,
            file_name=map_filename,
            mime="text/html"
        )

    shareByEmail(itinerary)
