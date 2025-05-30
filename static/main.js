let map;
let markers = [];
let demands = [];
let locations = [];
let depotSet = false;
let directionsServices = [];
let directionsRenderers = [];
let selectedAlgorithm = "nearest"; // default


function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 37.7749, lng: -122.4194 }, // Default to San Francisco
    zoom: 12,
    disableDefaultUI: true,
    mapId: "2b36dec94b5740e749f359f5",
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
    if (demands.length == 9){
      alert("Google API limits the number of markers to 10 so no more customers can be added.");
      return;
    }

    const customerIndex = demands.length + 1;
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
    reverseGeocode(latLng, (address) => {
      addMarkerCard(customerIndex, demand, address);
    });

  });

}

function setupAlgorithmSelector() {
  const boxes = document.querySelectorAll('.algo-box');
  boxes.forEach(box => {
    box.addEventListener('click', () => {
      boxes.forEach(b => b.classList.remove('selected'));
      box.classList.add('selected');
      selectedAlgorithm = box.getAttribute('data-algo');
    });
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
    body: JSON.stringify({ locations, demands, capacity, algorithm: selectedAlgorithm }),
  })
  .then(res => {
    if (!res.ok) throw new Error("Server error");
    return res.json();
  })
  .then(routes => {
    clearRoutes();
    routes.forEach((route, i) => {
      // Build full route: depot (0) at start and end
      const fullRoute = [0, ...route, 0];
      drawRoute(fullRoute, i);
    });
  })
  .catch(err => {
    console.error(err);
    alert("Error solving CVRP. See console for details.");
  });
}

// Clear existing directions/renderers
function clearRoutes() {
  directionsRenderers.forEach(renderer => renderer.setMap(null));
  directionsServices = [];
  directionsRenderers = [];
}

// Draw route on map using DirectionsService
function drawRoute(routeIndices, index) {
  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer({
    map,
    suppressMarkers: true,
    polylineOptions: {
      strokeColor: getColor(index),
      strokeWeight: 4,
    },
  });

  // Build waypoints excluding first and last
  const waypoints = routeIndices.slice(1, -1).map(idx => ({
    location: { lat: locations[idx][0], lng: locations[idx][1] },
    stopover: true,
  }));

  directionsService.route({
    origin: { lat: locations[routeIndices[0]][0], lng: locations[routeIndices[0]][1] },
    destination: { lat: locations[routeIndices[routeIndices.length - 1]][0], lng: locations[routeIndices[routeIndices.length - 1]][1] },
    waypoints,
    travelMode: google.maps.TravelMode.DRIVING,
  }, (result, status) => {
    if (status === 'OK') {
      directionsRenderer.setDirections(result);
      directionsServices.push(directionsService);
      directionsRenderers.push(directionsRenderer);
    } else {
      console.error('Directions request failed due to ' + status);
    }
  });
}

function getColor(index) {
  const colors = ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#00FFFF'];
  return colors[index % colors.length];
}

function createCircleElement(color, size, letter) {
  const div = document.createElement("div");
  div.style.backgroundColor = color;
  div.style.width = `${size}px`;
  div.style.height = `${size}px`;
  div.style.borderRadius = "50%";
  div.style.display = "flex";
  div.style.alignItems = "center";
  div.style.justifyContent = "center";
  div.style.color = "#ffffff";
  div.style.fontWeight = "bold";
  div.style.fontSize = `${size / 2}px`;
  div.style.border = "2px solid white"; // optional: border to improve visibility
  div.innerText = letter;
  return div;
}

function addDepotCard(address = "") {
  const container = document.getElementById("markers");
  const card = document.createElement("div");
  card.className = "marker-card";
  card.id = "marker-card-0";
  card.innerHTML = `
    <strong>Depot</strong><br>
    Address: ${address}<br>
  `;
  container.appendChild(card);
}


function addMarkerCard(index, demand, address = "") {
  const container = document.getElementById("markers");
  const card = document.createElement("div");
  card.className = "marker-card";
  card.id = `marker-card-${index}`;

  const lat = locations[index][0].toFixed(5);
  const lng = locations[index][1].toFixed(5);

  const info = document.createElement("div");
  info.innerHTML = `
    <strong>Customer ${index}</strong><br>
    Demand: ${demand}<br>
    Address: ${address}<br>
  `;

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "×";
  deleteBtn.className = "delete-btn";
  deleteBtn.onclick = () => deleteMarker(index);

  card.appendChild(info);
  card.appendChild(deleteBtn);
  container.appendChild(card);
}


function deleteMarker(index) {
  const markerIdx = index; // index in array is the same as demand order
  const marker = markers[markerIdx];

  if (marker) {
    marker.map = null; // remove from map
    markers.splice(markerIdx, 1);
    demands.splice(markerIdx - 1, 1);
    locations.splice(markerIdx, 1);
    depotSet = true; // keep depot as is

    const card = document.getElementById(`marker-card-${index}`);
    if (card) card.remove();

    // Rebuild marker cards since indices changed
    rebuildMarkerCards();
  }
}

function rebuildMarkerCards() {
  const container = document.getElementById("markers");
  container.innerHTML = "";

  for (let i = 1; i < markers.length; i++) {
    const latLng = new google.maps.LatLng(locations[i][0], locations[i][1]);
    reverseGeocode(latLng, (address) => {
      addMarkerCard(i, demands[i - 1], address);
    });
  }
}


function reverseGeocode(latLng, callback) {
  const geocoder = new google.maps.Geocoder();
  geocoder.geocode({ location: latLng }, (results, status) => {
    if (status === 'OK' && results[0]) {
      callback(results[0].formatted_address);
    } else {
      callback("Address not found");
    }
  });
}





window.onload = () => {
  setupAlgorithmSelector();
};
window.initMap = initMap;
window.solveCVRP = solveCVRP;

