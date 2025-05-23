let map;
let markers = [];
let demands = [];
let locations = [];
let depotSet = false;

// Utility: create a colored circle DIV (can embed text)
function createCircleElement(color, size = 24, text = "") {
  const div = document.createElement("div");
  Object.assign(div.style, {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: color,
    borderRadius: "50%",
    border: "2px solid white",
    boxSizing: "border-box",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#fff",
    fontSize: `${size / 2.5}px`,
    fontWeight: "bold",
    userSelect: "none",
  });
  if (text) div.textContent = text;
  return div;
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 40.0, lng: -100.0 },
    zoom: 4,
    mapId: "2b36dec94b5740e749f359f5",  // ← your Map ID here
  });

  map.addListener("click", (e) => {
    const latLng = e.latLng;

    if (!depotSet) {
      // --- Set Depot ---
      const depotEl = createCircleElement("#000000", 28, "D");
      const depotMarker = new google.maps.marker.AdvancedMarkerElement({
        position: latLng,
        map,
        element: depotEl,
        title: "Depot",
      });

      // Put depot at front of arrays
      markers.unshift(depotMarker);
      locations.unshift([latLng.lat(), latLng.lng()]);
      depotSet = true;
      alert("Depot set! Now click to add customers.");
      return;
    }

    // --- Add Customer ---
    const input = prompt("Enter demand for this customer:");
    const demand = parseInt(input, 10);
    if (isNaN(demand) || demand < 0) {
      alert("Invalid demand; please enter a non-negative integer.");
      return;
    }

    const custEl = createCircleElement("#007bff", 24, String(demand));
    const custMarker = new google.maps.marker.AdvancedMarkerElement({
      position: latLng,
      map,
      element: custEl,
      title: `Customer demand: ${demand}`,
    });

    markers.push(custMarker);
    demands.push(demand);
    locations.push([latLng.lat(), latLng.lng()]);
  });
}

function solveCVRP() {
  if (!depotSet) {
    alert("Please set a depot first by clicking on the map.");
    return;
  }

  const capInput = document.getElementById("capacityInput").value;
  const capacity = parseInt(capInput, 10);
  if (isNaN(capacity) || capacity <= 0) {
    alert("Enter a valid truck capacity.");
    return;
  }

  fetch("/solve", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ locations, demands, capacity }),
  })
  .then(res => {
    if (!res.ok) throw new Error("Server error");
    return res.json();
  })
  .then(routes => {
    // Clear existing polylines (optional)
    markers.forEach(m => {
      if (m.polyline) {
        m.polyline.setMap(null);
      }
    });

    // Draw new routes
    routes.forEach((route, i) => {
      const path = route.map(idx => ({
        lat: locations[idx][0],
        lng: locations[idx][1]
      }));

      const line = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor: getColor(i),
        strokeOpacity: 1.0,
        strokeWeight: 4,
        map: map
      });

      // Keep reference so you can clear later
      markers[i].polyline = line;
    });
  })
  .catch(err => {
    console.error(err);
    alert("Error solving CVRP. See console for details.");
  });
}

function getColor(index) {
  const colors = ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#00FFFF'];
  return colors[index % colors.length];
}

window.initMap = initMap;
window.solveCVRP = solveCVRP;
