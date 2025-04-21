import os
import random
import yaml
import requests
from pathlib import Path

# ⚙️ Configuración general
GENDER = "male"  # Cambia a "female" si querés solo mujeres

POSITION_DISTRIBUTION = {
    "GK": 2, "CB": 4, "LB": 1, "RB": 1,
    "CM": 4, "CDM": 1, "CAM": 1,
    "LM": 1, "RM": 1,
    "ST": 3, "CF": 1, "LW": 1, "RW": 1
}

FEET = ["right", "left", "both"]

def get_random_name(gender="male"):
    try:
        url = f"https://randomuser.me/api/?nat=es&gender={gender}"
        response = requests.get(url)
        if response.status_code == 200:
            user = response.json()["results"][0]["name"]
            return f"{user['first'].capitalize()} {user['last'].capitalize()}"
    except:
        pass
    return f"Jugador{random.randint(1000, 9999)}"

def generate_players():
    players = []
    numbers = random.sample(range(1, 100), sum(POSITION_DISTRIBUTION.values()))
    idx = 0
    for pos, count in POSITION_DISTRIBUTION.items():
        for _ in range(count):
            players.append({
                "name": get_random_name(GENDER),
                "gender": GENDER,
                "number": numbers[idx],
                "position": pos,
                "role": "starter" if _ < count - 1 else "substitute",
                "age": random.randint(18, 36),
                "height": round(random.uniform(1.65, 1.95), 2),
                "weight": random.randint(60, 90),
                "nationality": "Hoso",
                "foot": random.choice(FEET),
                "skill_rating": random.randint(60, 90),
                "morale": random.randint(60, 100),
                "status": {
                    "injured": False, "suspended": False,
                    "fitness": random.randint(85, 100),
                    "yellow_cards": 0, "red_cards": 0,
                    "injury_days_left": 0, "suspension_matches_left": 0
                },
                "stats": {
                    "matches_played": 0, "goals": 0, "assists": 0,
                    "yellow_cards_total": 0, "red_cards_total": 0,
                    "shots": 0, "passes_completed": 0,
                    "tackles": 0, "saves": 0, "clean_sheets": 0,
                    "minutes_played": 0
                }
            })
            idx += 1
    return {"players": players}

# 📁 Ruta base de los equipos
teams_path = Path("leagues/PDH/teams")

for team_folder in teams_path.iterdir():
    if team_folder.is_dir():
        players_data = generate_players()
        with open(team_folder / "players.yml", "w", encoding="utf-8") as f:
            yaml.dump(players_data, f, allow_unicode=True)

print("✅ Jugadores generados para todos los equipos (solo género:", GENDER, ")")
