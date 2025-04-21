import random
import yaml
from pathlib import Path
from datetime import date

LEAGUE_PATH = Path("leagues/PDH")
SCHEDULE_PATH = LEAGUE_PATH / "schedule.yml"
CONFIG_PATH = LEAGUE_PATH / "config.yml"
TEAMS_DIR = LEAGUE_PATH / "teams"
RESULTS_DIR = LEAGUE_PATH / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

EVENT_PROBABILITIES = config.get("match_simulation", {}).get("event_probabilities", {})
EVENT_PROBABILITIES = {k: float(v) for k, v in EVENT_PROBABILITIES.items()}
FATIGUE_ENABLED = config.get("match_simulation", {}).get("fatigue_enabled", True)
FATIGUE_FACTOR = float(config.get("match_simulation", {}).get("fatigue_factor", 0.2))
OVERTIME_CHANCE = float(config.get("match_simulation", {}).get("overtime_chance", 0.05))
PENALTY_CHANCE_FROM_FOUL = float(config.get("match_simulation", {}).get("penalty_chance_from_foul", 0.1))
ROUND_KEY = config.get("schedule_key", "round")


def load_team_players(team_slug):
    path = TEAMS_DIR / team_slug / "players.yml"
    if not path.exists():
        return [], []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["players"]
        starters = [p for p in data if p["role"] == "starter"]
        substitutes = [p for p in data if p["role"] == "substitute"]
        return starters, substitutes


def choose_player(players, event_type):
    if event_type == "goal":
        weighted = [p for p in players if p["position"] not in ["GK", "CB", "RB", "LB"]]
        if not weighted:
            weighted = players
        return random.choice(weighted)
    elif event_type == "save":
        gks = [p for p in players if p["position"] == "GK"]
        return random.choice(gks) if gks else random.choice(players)
    else:
        return random.choice(players)


def simulate_minute_by_minute(home, away, lineups, benches):
    duration = 90
    if random.random() < OVERTIME_CHANCE:
        duration = random.randint(91, 95)

    events = []
    minute_log = []
    ball_zone = 3
    team_in_possession = random.choice([home, away])
    active_players = {home: lineups[home][:], away: lineups[away][:]}

    def adjust_prob(base, zone):
        return base * {1: 3, 2: 2, 3: 1, 4: 0.5, 5: 0.1}.get(zone, 1)

    def occurs(event_type, zone):
        base = EVENT_PROBABILITIES.get(event_type, 0)
        fatigue = 1 + (minute / 90) * FATIGUE_FACTOR if FATIGUE_ENABLED else 1
        return random.random() < adjust_prob(base, zone) * fatigue

    for minute in range(1, duration + 1):
        other_team = away if team_in_possession == home else home
        move = random.choice([-1, 0, 1])
        ball_zone = max(1, min(5, ball_zone - move if team_in_possession == home else ball_zone + move))

        minute_entry = {
            "minute": minute,
            "team_in_possession": team_in_possession,
            "ball_zone": ball_zone
        }

        if occurs("goal", ball_zone) and ball_zone == 1:
            scorer = choose_player(active_players[team_in_possession], "goal")
            event = {"minute": minute, "team": team_in_possession, "type": "goal", "player": scorer["name"]}
            events.append(event)
            minute_entry["event"] = event

        elif occurs("foul", ball_zone):
            player = choose_player(active_players[team_in_possession], "foul")
            foul_event = {
                "minute": minute,
                "team": team_in_possession,
                "type": "foul",
                "player": player["name"]
            }

            yellow = random.random() < EVENT_PROBABILITIES.get("yellow_card", 0.1)
            red = random.random() < EVENT_PROBABILITIES.get("red_card", 0.05)

            print(f"🟡 {player['name']} recibió una tarjeta amarilla" if yellow else "🟥 Tarjeta roja" if red else "⚪ Sin tarjeta")

            if yellow:
                foul_event["card"] = "yellow"
                player["status"]["yellow_cards"] += 1

                if player["status"]["yellow_cards"] >= 2:
                    foul_event["card"] = "red"
                    player["status"]["red_cards"] += 1
                    active_players[team_in_possession].remove(player)
            elif red:
                foul_event["card"] = "red"
                player["status"]["red_cards"] += 1
                active_players[team_in_possession].remove(player)

            events.append(foul_event)
            minute_entry["event"] = foul_event

            if ball_zone == 1 and random.random() < PENALTY_CHANCE_FROM_FOUL:
                shooter = choose_player(active_players[team_in_possession], "goal")
                pen_event = {
                    "minute": minute,
                    "team": team_in_possession,
                    "type": "penalty",
                    "player": shooter["name"]
                }
                goal_event = {
                    "minute": minute,
                    "team": team_in_possession,
                    "type": "goal",
                    "player": shooter["name"],
                    "from_penalty": True
                }
                events += [pen_event, goal_event]
                minute_entry["event"] = goal_event

        elif occurs("corner", ball_zone) and ball_zone <= 2:
            event = {"minute": minute, "team": team_in_possession, "type": "corner"}
            events.append(event)
            minute_entry["event"] = event

        elif occurs("offside", ball_zone) and ball_zone <= 2:
            event = {"minute": minute, "team": team_in_possession, "type": "offside"}
            events.append(event)
            minute_entry["event"] = event

        if occurs("injury", ball_zone):
            injured = choose_player(active_players[team_in_possession], "injury")
            print(f"🟠 Lesión de {injured['name']}, suplentes disponibles: {len(benches[team_in_possession])}")

            if injured in active_players[team_in_possession]:
                events.append({
                    "minute": minute,
                    "team": team_in_possession,
                    "type": "injury",
                    "player": injured["name"]
                })
                if benches[team_in_possession]:
                    sub = benches[team_in_possession].pop(0)
                    active_players[team_in_possession].remove(injured)
                    active_players[team_in_possession].append(sub)
                    events.append({
                        "minute": minute,
                        "team": team_in_possession,
                        "type": "substitution",
                        "player_out": injured["name"],
                        "player_in": sub["name"],
                        "reason": "injury"
                    })

        minute_log.append(minute_entry)
        if random.random() < 0.2:
            team_in_possession = other_team

    return events, minute_log


def count_goals(events, team):
    return sum(1 for e in events if e["type"] == "goal" and e["team"] == team)


def simulate_jornada(jornada_id, jornada_matches):
    simulated_matches = []
    for match in jornada_matches:
        home = match["home"]
        away = match["away"]
        lineups = {}
        benches = {}
        for team in [home, away]:
            slug = team.lower().replace(" ", "")
            starters, subs = load_team_players(slug)
            lineups[team] = starters
            benches[team] = subs

        events, minute_log = simulate_minute_by_minute(home, away, lineups, benches)
        goals_home = count_goals(events, home)
        goals_away = count_goals(events, away)
        simulated_matches.append({
            "home": home,
            "away": away,
            "goals_home": goals_home,
            "goals_away": goals_away,
            "events": events,
            "possession_log": minute_log
        })
    return {
        "jornada": jornada_id,
        "date": str(date.today()),
        "matches": simulated_matches
    }


if __name__ == "__main__":
    if not SCHEDULE_PATH.exists():
        print(f"❌ No se encontró el archivo de programación: {SCHEDULE_PATH}")
        exit(1)

    with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
        schedule_data = yaml.safe_load(f)
        schedule = schedule_data.get(ROUND_KEY, {})

    if not schedule:
        print(f"❌ No se encontraron partidos para la jornada: {ROUND_KEY}")
        exit(1)

    for jornada_id, matches in schedule.items():
        result_file = RESULTS_DIR / f"{jornada_id}.yml"
        if not result_file.exists():
            jornada_result = simulate_jornada(jornada_id, matches)
            with open(result_file, "w", encoding="utf-8") as f:
                yaml.dump(jornada_result, f, allow_unicode=True)
            print(f"✅ {jornada_id} simulada con posesión y zonas.")
            break
        else:
            print(f"⏭️  {jornada_id} ya existe, se omite.")