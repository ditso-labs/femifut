(async () => {
    // 1️⃣ Detectar slug de liga desde URL
    const url = new URL(window.location.href);
    // Primero intenta ?league=PDH, luego toma el último segmento del path
    const leagueSlug = url.searchParams.get("league")
      || url.pathname.replace(/\/$/, "").split("/").pop()
      || "PDH";  // fallback
  
    // 2️⃣ Construir rutas dinámicas
    const baseDir    = `../leagues/${leagueSlug}`;
    const statsFile  = `${baseDir}/stats.yaml`;
    const teamsDir   = `${baseDir}/teams`;
  
    // 3️⃣ Cargar estadísticas y nombres de equipo
    const response   = await fetch(statsFile);
    const statsYaml  = await response.text();
    const stats      = jsyaml.load(statsYaml).stats;
    const teamSlugs  = Object.keys(stats);
    const teamNames  = {};
  
    await Promise.all(teamSlugs.map(async slug => {
      try {
        const res      = await fetch(`${teamsDir}/${slug}/team.yml`);
        const teamYaml = await res.text();
        const data     = jsyaml.load(teamYaml);
        teamNames[slug] = data.name || slug;
      } catch {
        console.warn(`No se pudo cargar team.yml de ${slug}`);
        teamNames[slug] = slug;
      }
    }));
  
    // 4️⃣ Renderizar tabla
    const rows = Object.entries(stats).map(([slug, data]) => ({
      nombre: teamNames[slug],
      ...data
    }));
    rows.sort((a, b) =>
      b.points - a.points ||
      b.goal_difference - a.goal_difference ||
      b.goals_for - a.goals_for
    );
  
    const tbody = document.querySelector("#tabla tbody");
    rows.forEach(eq => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${eq.nombre}</td>
        <td>${eq.played}</td>
        <td>${eq.wins}</td>
        <td>${eq.draws}</td>
        <td>${eq.losses}</td>
        <td>${eq.goals_for}</td>
        <td>${eq.goals_against}</td>
        <td>${eq.goal_difference}</td>
        <td>${eq.points}</td>
      `;
      tbody.appendChild(tr);
    });
  })();
  