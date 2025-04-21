(async () => {
    // 1️⃣ Detectar slug de liga desde URL
    const url = new URL(window.location.href);
    const leagueSlug = url.searchParams.get("league")
      || url.pathname.replace(/\/$/, "").split("/").pop()
      || "PDH";  // fallback
  
    // 2️⃣ Construir rutas dinámicas
    const baseDir       = `data/${leagueSlug}`;
    const statsFile     = `${baseDir}/stats.yaml`;
    const teamsListFile = `${baseDir}/teams_list.yaml`;
  
    // 3️⃣ Cargar estadísticas
    const respStats  = await fetch(statsFile);
    const textStats  = await respStats.text();
    const stats      = jsyaml.load(textStats).stats;
    const slugs      = Object.keys(stats);
  
    // 4️⃣ Cargar lista de equipos y generar el mapeo slug → nombre real
    const respTeamsList = await fetch(teamsListFile);
    const textTeamsList = await respTeamsList.text();
    const teamsListData = jsyaml.load(textTeamsList).teams;
    const teamNames     = {};
  
    teamsListData.forEach(fullName => {
      // Generamos el mismo slug que usamos en stats:
      const slug = fullName
        .toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // quitar tildes
        .replace(/[^a-z0-9]/g, "");                      // quitar espacios y símbolos
  
      teamNames[slug] = fullName;
    });
  
    // Para seguridad: cualquier slug faltante, lo mostramos tal cual
    slugs.forEach(s => {
      if (!teamNames[s]) teamNames[s] = s;
    });
  
    // 5️⃣ Renderizar tabla
    const rows = slugs.map(slug => ({
      nombre: teamNames[slug],
      ...stats[slug]
    })).sort((a, b) =>
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
  