import os
import yaml
from pathlib import Path

# 📦 Carga la lista de equipos desde el YAML
def load_team_names(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("teams", [])

def slugify(name):
    return name.lower()\
               .replace(" ", "")\
               .replace("á", "a")\
               .replace("é", "e")\
               .replace("í", "i")\
               .replace("ó", "o")\
               .replace("ú", "u")\
               .replace("ñ", "n")

def generate_team_yaml(team_name):
    slug = slugify(team_name)
    return {
        "name": team_name,
        "short_name": ''.join([word[0] for word in team_name.split()]).upper(),
        "slug": slug,
        "abbreviation": ''.join([word[0] for word in team_name.split()]).upper(),
        "city": "Ciudad Genérica",
        "stadium": f"Estadio {team_name.split()[0]}",
        "founded": 1980 + hash(team_name) % 40,
        "coach": "Nombre del Entrenador",
        "colors": {
            "primary": "#0000FF",
            "secondary": "#FFFFFF"
        },
        "logo": f"media/{slug}_logo.png",
        "rivalries": [],
        "fans": {
            "nickname": f"La Hinchada de {team_name}",
            "estimated_fanbase": 50000 + hash(team_name) % 50000
        },
        "budget": {
            "currency": "CRC",
            "amount": 200_000_000 + (hash(team_name) % 100_000_000)
        },
        "history": {
            "championships": hash(team_name) % 10,
            "last_title": 2000 + hash(team_name) % 24
        },
        "social": {
            "twitter": f"@{slug}",
            "website": f"https://{slug}.hoso",
            "instagram": f"@{slug}_oficial"
        }
    }

def main():
    list_path = Path("leagues/PDH/teams_list.yml")
    base_path = Path("leagues/PDH/teams")
    base_path.mkdir(parents=True, exist_ok=True)

    team_names = load_team_names(list_path)

    for team_name in team_names:
        team_folder = base_path / slugify(team_name)
        team_folder.mkdir(parents=True, exist_ok=True)
        team_data = generate_team_yaml(team_name)
        with open(team_folder / "team.yml", "w", encoding="utf-8") as f:
            yaml.dump(team_data, f, allow_unicode=True)

    print("✅ Equipos generados a partir de teams_list.yml.")

if __name__ == "__main__":
    main()
