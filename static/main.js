let map;
let markers = [];
let demands = [];
let locations = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 40.0, lng: -100.0 },
        zoom: 4,
    });

    map.addListener("click", (e) => {
        const latLng = e.latLng;
        const demand = parseInt(prompt("Enter demand for this location:"), 10);
        if (isNaN(demand)) return;

        const marker = new google.maps.Marker({
            position: latLng,
            map: map,
            label: `${demand}`,
        });

        markers.push(marker);
        demands.push(demand);
        locations.push([latLng.lat(), latLng.lng()]);
    });
}

function solveCVRP() {
    const capacity = parseInt(document.getElementById("capacityInput").value, 10);
    if (isNaN(capacity)) {
        alert("Enter valid capacity");
        return;
    }

    fetch("/solve", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ locations, demands, capacity }),
    })
    .then(res => res.json())
    .then(routes => {
        console.log("Routes:", routes);
        routes.forEach((route, i) => {
            const path = route.map(idx => ({
                lat: locations[idx][0],
                lng: locations[idx][1]
            }));

            new google.maps.Polyline({
                path,
                geodesic: true,
                strokeColor: getColor(i),
                strokeOpacity: 1.0,
                strokeWeight: 4,
                map: map
            });
        });
    });
}

function getColor(index) {
    const colors = ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#00FFFF'];
    return colors[index % colors.length];
}

window.initMap = initMap;
