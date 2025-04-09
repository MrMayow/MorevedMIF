const map = L.map("map").setView([initialCoords.lat, initialCoords.lon], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

const marker = L.marker([initialCoords.lat, initialCoords.lon]).addTo(map);

async function refreshCoords() {
    const res = await fetch("/get_coords");
    const data = await res.json();
    marker.setLatLng([data.lat, data.lon]);
    map.setView([data.lat, data.lon]);
}

setInterval(refreshCoords, 3000);

// Обработка формы маршрута
document.getElementById("route-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const input = document.getElementById("route-input").value;

    let route;
    try {
        route = JSON.parse(input);
    } catch (err) {
        alert("Invalid JSON format.");
        return;
    }

    const response = await fetch("/submit_route", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ route: route })
    });

    const result = await response.json();
    alert(result.status);
});
