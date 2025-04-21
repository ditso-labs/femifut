import yaml
from pathlib import Path

# Función para normalizar nombres
def slugify(name):
    return name.lower().replace(" ", "").replace("á", "a").replace("é", "e")\
               .replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

# Leer lista de equipos
with open("leagues/PDH/teams_list.yml", "r", encoding="utf-8") as f:
    teams = yaml.safe_load(f)["teams"]

# Generar estadísticas con slugs como claves
stats = {}
for team in teams:
    slug = slugify(team)
    stats[slug] = {
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0
    }

# Guardar archivo
stats_path = Path("leagues/PDH/stats.yaml")
with open(stats_path, "w", encoding="utf-8") as f:
    yaml.dump({"stats": stats}, f, allow_unicode=True)

"✅ stats.yaml generado con nombres normalizados (slug)."
