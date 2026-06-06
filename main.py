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

    <h3>Preferences</h3>

    Max duration (hours)<br>
    <input id="duration" type="number" value="3"><br><br>

    Difficulty<br>
    <select id="difficulty">
      <option value="easy">Easy</option>
      <option value="medium">Medium</option>
      <option value="hard">Hard</option>
    </select><br><br>

    Baby friendly
    <input id="baby" type="checkbox"><br><br>

    Preferences<br>
    <input type="checkbox" id="lake"> Lake<br>
    <input type="checkbox" id="panorama"> Panorama<br><br>

    <button onclick="findTrails()">Find Trekking</button>

    <hr>

    <div id="results"></div>

    <script>

    async function findTrails(){

        const duration = document.getElementById("duration").value
        const difficulty = document.getElementById("difficulty").value
        const baby = document.getElementById("baby").checked
        const lake = document.getElementById("lake").checked
        const panorama = document.getElementById("panorama").checked

        const res = await fetch(`/recommend?duration=${duration}&difficulty=${difficulty}&baby=${baby}&lake=${lake}&panorama=${panorama}`)

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
def recommend(duration: float, difficulty: str, baby: bool, lake: bool, panorama: bool):

    results = []

    for r in routes:

        if r["duration"] > duration:
            continue

        if baby and not r.get("baby_friendly", False):
            continue

        if lake and not r.get("lake", False):
            continue

        if panorama and not r.get("panorama", False):
            continue

        temp = get_weather(r["lat"], r["lon"])

        results.append({
            "name": r["name"],
            "duration": r["duration"],
            "temp": temp,
            "info": r["info"],
            "map": r["map"]
        })

    return results
