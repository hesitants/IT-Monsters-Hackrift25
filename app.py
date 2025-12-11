from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
import random



# ------------------------------
# FastAPI app setup
# ------------------------------

app = FastAPI(
    title="ZenFlow Stress API",
    description="Simple stress score + intervention backend",
    version="1.0.0",
)

# Allow frontend (React / others) to call this API from another port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ========== Dashboard route (chart page) ==========
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    chart_data = {
        "labels": ["😭", "🥰", "😐", "😡", " 😮"], 
        "allocated": [80, 90, 70, 85, 60],
        "actual": [70, 95, 60, 75, 50],
    }

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "data": chart_data},
    )

# ------------------------------
# Data model for incoming JSON
# ------------------------------

class StressData(BaseModel):
    """
    Incoming data from the frontend.

    - mood: 0–100 (0 = very bad, 100 = very good)
    - screen_time: hours spent on screens today
    - typing_speed: words per minute
    """
    mood: int            # 0-100
    screen_time: float   # hours
    typing_speed: int    # wpm


# ------------------------------
# Core functions (logic layer)
# ------------------------------

def calculate_stress_score(mood: int, screen_time: float, typing_speed: int) -> float:
    mood_component = 100 - mood  # fix: high mood lowers stress
    screen_component = screen_time * 10
    typing_component = abs(100 - typing_speed)

    stress_score = (
        0.5 * mood_component +
        0.3 * screen_component +
        0.2 * typing_component
    )

    return round(stress_score, 2)

def choose_intervention(score: float) -> str:
    calm = ["You're calm! Keep it up.", "Everything seems smooth — enjoy the moment.", "Great job staying relaxed today!"]
    light = ["Try a quick 1-minute breathing exercise.", "Stretch your arms and shoulders for a minute.", "Take a short walk around the room."]
    medium = ["Take a 3-minute break away from your screen.", "Listen to a relaxing song.", "Try a short guided meditation."]
    high = ["High stress detected — take a 5-minute walk or hydration break.", "Step outside for fresh air and deep breaths.", "Do a short body scan to release tension."]
    
    if score < 30:
        return random.choice(calm)
    elif score < 60:
        return random.choice(light)
    elif score < 80:
        return random.choice(medium)
    else:
        return random.choice(high)
    
# ------------------------------
# API routes
# ------------------------------

@app.get("/")
def read_root():
    """
    Simple welcome route to test if the server is running.
    """
    return {"message": "ZenFlow Stress API is running."}


@app.post("/stress")
def calculate_stress(data: StressData):
    """
    Main endpoint used by your frontend.

    Request JSON:
    {
        "mood": 50,
        "screen_time": 1.5,
        "typing_speed": 80
    }

    Response JSON:
    {
        "stress_score": 42.35,
        "intervention": "Try a quick 1-minute breathing exercise."
    }
    """
    score = calculate_stress_score(
        mood=data.mood,
        screen_time=data.screen_time,
        typing_speed=data.typing_speed,
    )

    intervention = choose_intervention(score)

    return {
        "stress_score": score,
        "intervention": intervention,
    }


# Optional: a dedicated intervention endpoint (if you want)
@app.post("/intervention")
def get_intervention(data: StressData):
    """
    Alternative endpoint:
    - Takes the same input as /stress
    - Returns only the intervention message
    """
    score = calculate_stress_score(
        mood=data.mood,
        screen_time=data.screen_time,
        typing_speed=data.typing_speed,
    )
    intervention = choose_intervention(score)

    return {"intervention": intervention, "score": score}


# ------------------------------
# Local dev entrypoint
# ------------------------------

if __name__ == "__main__":
    # This lets you run the server with:  python app.py
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,   # auto-reload on code changes (great for development)
    )

