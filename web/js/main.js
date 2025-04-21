fetch("../leagues/PDH/stats.yaml")
  .then(res => res.text())
  .then(yamlText => {
    const data = jsyaml.load(yamlText).stats;
    const rows = Object.entries(data).map(([slug, stats]) => ({
      nombre: slug.replace(/([a-z])([A-Z])/g, "$1 $2"), // puedes mejorar esto
      ...stats
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
