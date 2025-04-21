import yaml
from pathlib import Path
from tabulate import tabulate

# Archivos
SCHEDULE_FILE = Path("leagues/PDH/schedule.yml")
RESULTS_DIR = Path("leagues/PDH/results")
STATS_FILE = Path("leagues/PDH/stats.yaml")
TEAMS_DIR = Path("leagues/PDH/teams")

# Cargar nombres reales de los equipos
def get_team_names():
    names = {}
    for team_dir in TEAMS_DIR.iterdir():
        info_file = team_dir / "team.yml"
        if info_file.exists():
            with open(info_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                names[team_dir.name] = data.get("name", team_dir.name)
        else:
            names[team_dir.name] = team_dir.name
    return names

team_names = get_team_names()

# Cargar estadísticas existentes
with open(STATS_FILE, "r", encoding="utf-8") as f:
    stats_data = yaml.safe_load(f)
stats = stats_data["stats"]

# Reiniciar estadísticas
for team_stats in stats.values():
    team_stats.update({
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0
    })

# Procesar resultados
for result_file in sorted(RESULTS_DIR.glob("*.yml")):
    with open(result_file, "r", encoding="utf-8") as f:
        jornada_data = yaml.safe_load(f)

    for match in jornada_data.get("matches", []):
        home = match["home"]
        away = match["away"]
        goals_home = match["goals_home"]
        goals_away = match["goals_away"]

        stats[home]["played"] += 1
        stats[away]["played"] += 1

        stats[home]["goals_for"] += goals_home
        stats[home]["goals_against"] += goals_away
        stats[away]["goals_for"] += goals_away
        stats[away]["goals_against"] += goals_home

        stats[home]["goal_difference"] = stats[home]["goals_for"] - stats[home]["goals_against"]
        stats[away]["goal_difference"] = stats[away]["goals_for"] - stats[away]["goals_against"]

        if goals_home > goals_away:
            stats[home]["wins"] += 1
            stats[home]["points"] += 3
            stats[away]["losses"] += 1
        elif goals_home < goals_away:
            stats[away]["wins"] += 1
            stats[away]["points"] += 3
            stats[home]["losses"] += 1
        else:
            stats[home]["draws"] += 1
            stats[away]["draws"] += 1
            stats[home]["points"] += 1
            stats[away]["points"] += 1

# Guardar archivo actualizado
with open(STATS_FILE, "w", encoding="utf-8") as f:
    yaml.dump({"stats": stats}, f, allow_unicode=True)

# Mostrar tabla ordenada
tabla = []
for slug, data in stats.items():
    tabla.append([
        team_names.get(slug, slug),
        data["played"],
        data["wins"],
        data["draws"],
        data["losses"],
        data["goals_for"],
        data["goals_against"],
        data["goal_difference"],
        data["points"]
    ])

tabla_ordenada = sorted(tabla, key=lambda x: (-x[8], -x[7], -x[5]))  # por puntos, diferencia, goles a favor

print(tabulate(
    tabla_ordenada,
    headers=["Equipo", "PJ", "G", "E", "P", "GF", "GC", "DG", "Pts"],
    tablefmt="fancy_grid"
))
