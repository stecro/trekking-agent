from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import requests

app = FastAPI()

with open("routes.json") as f:
    routes = json.load(f)

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max",
        "timezone": "auto"
    }

    data = requests.get(url, params=params).json()
    return data["daily"]["temperature_2m_max"][0]


@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <body style="font-family:Arial;margin:40px">

    <h1>Trentino Trekking Finder</h1>

    <button onclick="findTrails()">Find Trekking</button>

    <div id="results"></div>

    <script>

    async function findTrails(){

        const res = await fetch('/recommend')
        const data = await res.json()

        let html=""

        data.forEach(t => {

            html += `
            <h3>${t.name}</h3>
            Duration: ${t.duration} h<br>
            Temperature: ${t.temp}°C<br>

            <a href="${t.info}" target="_blank">Trail info</a><br>
            <a href="${t.map}" target="_blank">Map</a>

            <br><br>
            `

        })

        document.getElementById("results").innerHTML = html
    }

    </script>

    </body>
    </html>
    """


@app.get("/recommend")
def recommend():

    results = []

    for r in routes:

        temp = get_weather(r["lat"], r["lon"])

        results.append({
            "name": r["name"],
            "duration": r["duration"],
            "temp": temp,
            "info": r["info"],
            "map": r["map"]
        })

    return results
