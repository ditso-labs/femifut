const teamsDir = "../leagues/PDH/teams";
const statsFile = "../leagues/PDH/stats.yaml";

async function loadTeamNames() {
  const response = await fetch(statsFile);
  const statsYaml = await response.text();
  const stats = jsyaml.load(statsYaml).stats;

  const teamSlugs = Object.keys(stats);
  const teamNames = {};

  await Promise.all(teamSlugs.map(async (slug) => {
    try {
      const res = await fetch(`${teamsDir}/${slug}/team.yml`);
      const teamYaml = await res.text();
      const teamData = jsyaml.load(teamYaml);
      teamNames[slug] = teamData.name || slug;
    } catch (e) {
      console.warn(`No se pudo cargar nombre real de ${slug}`);
      teamNames[slug] = slug;
    }
  }));

  return { stats, teamNames };
}

loadTeamNames().then(({ stats, teamNames }) => {
  const rows = Object.entries(stats).map(([slug, data]) => ({
    nombre: teamNames[slug],
    ...data
  }));

  rows.sort((a, b) => b.points - a.points || b.goal_difference - a.goal_difference);

  const tbody = document.querySelector("#tabla tbody");
  rows.forEach(equipo => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${equipo.nombre}</td>
      <td>${equipo.played}</td>
      <td>${equipo.wins}</td>
      <td>${equipo.draws}</td>
      <td>${equipo.losses}</td>
      <td>${equipo.goals_for}</td>
      <td>${equipo.goals_against}</td>
      <td>${equipo.goal_difference}</td>
      <td>${equipo.points}</td>`;
    tbody.appendChild(tr);
  });
});
