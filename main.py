import os
import yaml

LEAGUE_PATH = "leagues/PDH"
TEAMS_DIR = os.path.join(LEAGUE_PATH, "teams")

teams_data = []

# Recorremos cada carpeta dentro de 'teams'
for team_folder in os.listdir(TEAMS_DIR):
    team_path = os.path.join(TEAMS_DIR, team_folder)

    if os.path.isdir(team_path):
        team_yaml_path = os.path.join(team_path, "team.yml")

        if os.path.isfile(team_yaml_path):
            with open(team_yaml_path, "r", encoding="utf-8") as f:
                team_data = yaml.safe_load(f)
                team_data["folder"] = team_folder
                teams_data.append(team_data)

# Mostrar equipos cargados
for team in teams_data:
    print(f"🏟️  {team['name']} ({team['short_name']}) - Ciudad: {team['city']}")
