import yaml
from pathlib import Path
import sys
from collections import defaultdict

RESULTS_DIR = Path("leagues/PDH/results")
TEAMS_DIR = Path("leagues/PDH/teams")

# Cargar nombres reales de equipos
def cargar_nombres_equipos():
    nombres = {}
    for team_dir in TEAMS_DIR.iterdir():
        team_file = team_dir / "team.yml"
        if team_file.exists():
            with open(team_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                nombres[team_dir.name] = data.get("name", team_dir.name)
        else:
            nombres[team_dir.name] = team_dir.name
    return nombres

team_names = cargar_nombres_equipos()

# Cargar resultado de jornada
def cargar_resultado(jornada_id):
    result_file = RESULTS_DIR / f"{jornada_id}.yml"
    if not result_file.exists():
        print(f"❌ No se encontró el archivo: {result_file}")
        sys.exit(1)

    with open(result_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Mostrar resumen por partido
def resumir_partido(match):
    home = match["home"]
    away = match["away"]
    home_name = team_names.get(home, home)
    away_name = team_names.get(away, away)

    print(f"\n⚽ {home_name} vs {away_name}")
    print(f"   🔢 Marcador final: {match['goals_home']} - {match['goals_away']}")

    eventos = match["events"]
    goles = defaultdict(int)
    lesiones = []
    tarjetas = []
    sustituciones = []

    for ev in eventos:
        tipo = ev["type"]
        jugador = ev.get("player")
        if tipo == "goal" and jugador:
            goles[jugador] += 1
        elif tipo == "injury":
            lesiones.append((ev["minute"], ev["team"], jugador))
        elif tipo in ["yellow_card", "red_card"]:
            tarjetas.append((tipo, ev["minute"], ev["team"], jugador))
        elif tipo == "substitution":
            sustituciones.append((ev["minute"], ev["team"], ev["player_out"], ev["player_in"]))

    if goles:
        print("   🎯 Goles:")
        for jugador, cantidad in goles.items():
            print(f"      - {jugador}: {cantidad} gol(es)")

    if tarjetas:
        print("   🟨🟥 Tarjetas:")
        for tipo, minuto, equipo, jugador in tarjetas:
            simbolo = "🟨" if tipo == "yellow_card" else "🟥"
            nombre_equipo = team_names.get(equipo, equipo)
            print(f"      - {simbolo} {jugador} ({nombre_equipo}) en el minuto {minuto}")

    if lesiones:
        print("   🤕 Lesiones:")
        for minuto, equipo, jugador in lesiones:
            nombre_equipo = team_names.get(equipo, equipo)
            print(f"      - {jugador} ({nombre_equipo}) lesionado al minuto {minuto}")

    if sustituciones:
        print("   🔄 Cambios:")
        for minuto, equipo, out_p, in_p in sustituciones:
            nombre_equipo = team_names.get(equipo, equipo)
            print(f"      - {nombre_equipo} minuto {minuto}: {out_p} ➡️ {in_p}")

# Resumen general
def resumir_jornada(jornada_id):
    datos = cargar_resultado(jornada_id)
    print(f"\n📅 Resumen de la Jornada {jornada_id} - Fecha: {datos['date']}")
    for partido in datos["matches"]:
        resumir_partido(partido)

if __name__ == "__main__":
    jornada_id = '5'  # o sys.argv[1]
    resumir_jornada(jornada_id)
