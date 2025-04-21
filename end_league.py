import yaml
from pathlib import Path

# 📁 Rutas de archivos
STATS_FILE = Path("leagues/PDH/stats.yaml")
TEAMS_FILE = Path("leagues/PDH/teams_list.yml")

# 📦 Cargar estadísticas con slugs
with open(STATS_FILE, "r", encoding="utf-8") as f:
    stats_data = yaml.safe_load(f)["stats"]

# 📦 Cargar lista de nombres reales
with open(TEAMS_FILE, "r", encoding="utf-8") as f:
    teams_list = yaml.safe_load(f)["teams"]

# 🔁 Función para slugify inverso
def slugify(name):
    return name.lower().replace(" ", "").replace("á", "a").replace("é", "e")\
               .replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

# 🧭 Crear diccionario slug → nombre
slug_to_name = {slugify(name): name for name in teams_list}

# 🧮 Convertir y ordenar
teams_stats = [(slug_to_name.get(slug, slug), data) for slug, data in stats_data.items()]
teams_sorted = sorted(
    teams_stats,
    key=lambda item: (
        item[1]["points"],
        item[1]["goal_difference"],
        item[1]["goals_for"]
    ),
    reverse=True
)

# 📊 Mostrar tabla
print("📊 Tabla de posiciones")
print(f"{'Pos':<4} {'Equipo':<25} {'Pts':<4} {'GD':<4} {'GF':<4}")
for i, (name, data) in enumerate(teams_sorted, 1):
    print(f"{i:<4} {name:<25} {data['points']:<4} {data['goal_difference']:<4} {data['goals_for']:<4}")

# 🏆 Campeón y ⬇️ Descenso
champion = teams_sorted[0][0]
relegated = teams_sorted[-1][0]
print(f"\n🏆 Campeón: {champion}")
print(f"⬇️ Desciende: {relegated}")
