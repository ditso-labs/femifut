import yaml
import os
from itertools import combinations

def generate_round_robin(teams, return_leg=False):
    if len(teams) % 2 != 0:
        teams.append("Descansa")  # añadir equipo fantasma para ligas impares

    jornadas = []
    n = len(teams)
    total_rounds = n - 1

    for i in range(total_rounds):
        jornada = []
        for j in range(n // 2):
            home = teams[j]
            away = teams[n - 1 - j]
            if home != "Descansa" and away != "Descansa":
                jornada.append({"home": home, "away": away})
        teams.insert(1, teams.pop())  # rotación de equipos
        jornadas.append(jornada)

    if return_leg:
        vuelta = []
        for jornada in jornadas:
            vuelta.append([
                {"home": match["away"], "away": match["home"]}
                for match in jornada
            ])
        jornadas += vuelta

    # Convertir a formato yaml
    schedule = {
        f"{i+1}": jornada
        for i, jornada in enumerate(jornadas)
    }

    return schedule

# Leer nombres de equipos desde carpetas en /leagues/PDH/teams/
teams_path = "leagues/PDH/teams"
team_names = [name for name in os.listdir(teams_path)
              if os.path.isdir(os.path.join(teams_path, name))]

# Generar calendario
calendar = generate_round_robin(team_names, return_leg=True)

# Guardar en YAML
with open("leagues/PDH/schedule.yml", "w", encoding="utf-8") as f:
    yaml.dump({"round": calendar}, f, allow_unicode=True)

print("📅 Calendario generado correctamente.")
