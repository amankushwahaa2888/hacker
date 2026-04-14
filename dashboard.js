async function loadAlerts() {
  const res = await fetch("http://localhost:5000/api/alerts");
  const alerts = await res.json();

  const container = document.getElementById("alerts");

  alerts.forEach(a => {
    const p = document.createElement("p");
    p.textContent = a.message;
    container.appendChild(p);
  });
}

loadAlerts();