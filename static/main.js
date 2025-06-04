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
  
      reverseGeocode(latLng, (address) => {
        addDepotCard(address, latLng);
      });
  
      alert("Depot set! Now click to add customers.");
      return;
    }
  
    const input = prompt("Enter demand for this customer:");
    const demand = parseInt(input, 10);
    if (isNaN(demand) || demand < 0) {
      alert("Invalid demand; please enter a non-negative integer.");
      return;
    }
    if (demands.length == 9) {
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
  //return jsonify(routes=routes, distance=distance)
  fetch("/solve", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ locations, demands, capacity, algorithm: selectedAlgorithm }),
  })
  .then(res => {
    if (!res.ok) throw new Error("Server error");
    return res.json();
  })
  .then(({ routes, distance }) => {
    clearRoutes();
  
    routes.forEach((route, i) => {
      const fullRoute = [0, ...route, 0];
      drawRoute(fullRoute, i);
    });
  
    showSolutionPopup(routes, distance);
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
function addDepotCard(address, latLng) {
  const container = document.getElementById("markers");

  const card = document.createElement("div");
  card.className = "marker-card depot-card";

  const lat = latLng.lat().toFixed(5);
  const lng = latLng.lng().toFixed(5);

  const info = document.createElement("div");
  info.innerHTML = `
    <strong>Depot</strong><br>
    Address: ${address}<br>
  `;

  card.appendChild(info);
  container.prepend(card); // insert at top
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

  // Add depot card (always at index 0)
  if (depotSet && locations.length > 0) {
    const depotLatLng = new google.maps.LatLng(locations[0][0], locations[0][1]);
    reverseGeocode(depotLatLng, (address) => {
      addDepotCard(address, depotLatLng);
    });
  }

  // Add customer cards (start from index 1)
  for (let i = 1; i < markers.length; i++) {
    const latLng = new google.maps.LatLng(locations[i][0], locations[i][1]);
    const demand = demands[i - 1]; // offset by 1 because depot is at 0
    reverseGeocode(latLng, (address) => {
      addMarkerCard(i, demand, address);
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
function resetMap() {
  // 1. Remove all markers from map
  markers.forEach(markerObj => {
    if (markerObj && markerObj.setMap) {
      // For AdvancedMarkerElement, setMap(null) removes it from the map
      markerObj.setMap(null);
    }
  });

  // 2. Reset internal data
  markers = [];
  demands = [];
  locations = [];
  depotSet = false;

  // 3. Clear any drawn routes on the map
  clearRoutes();

  // 4. Clear all “cards” in the #markers container
  const container = document.getElementById("markers");
  if (container) {
    container.innerHTML = "";
  }

}
function showSolutionPopup(routes, distance) {
  const solutionContainer = document.getElementById("solutionText");
  solutionContainer.innerHTML = ""; // Clear previous content

  if (!routes || routes.length === 0) {
    // If there are no routes, show a message
    const p = document.createElement("p");
    p.innerText = "No routes found.";
    solutionContainer.appendChild(p);
  } else {
    routes.forEach((route, i) => {
      // 1. Remove any “0” entries that might have been returned by the backend.
      //    (We want exactly one depot at start, one at end—no extras in between.)
      const sanitized = route.filter((idx) => idx !== 0);

      // 2. Build the “fullRoute” with exactly one 0 at start and one 0 at end,
      //    unless there are no customers, in which case we show just [0].
      let fullRoute;
      if (sanitized.length === 0) {
        // No customers assigned to this vehicle → show “Depot” only once
        fullRoute = [0];
      } else {
        fullRoute = [0, ...sanitized, 0];
      }

      // 3. Convert indices to labels (“Depot” or “Customer N”)
      const routeLabels = fullRoute.map((idx) =>
        idx === 0 ? "Depot" : `Customer ${idx}`
      );

      // 4. Create a <p> element to hold “Route i: Depot → Customer X → …”
      const p = document.createElement("p");
      p.innerText = `Route ${i + 1}: ${routeLabels.join(" → ")}`;

      // 5. Color this <p>’s text to match the map polyline color
      //    (getColor(i) returns a hex string, e.g. “#FF0000”)
      p.style.color = getColor(i);
      solutionContainer.appendChild(p);
    });

    // 6. Add a summary of total distance
    const distanceP = document.createElement("p");
    distanceP.innerText = `Total Distance: ${(distance / 1000).toFixed(2)} km`;
    distanceP.style.fontWeight = "bold";
    solutionContainer.appendChild(distanceP);



  }

  // 6. Finally, make the popup visible
  document.getElementById("solutionPopup").style.display = "block";
}
function closeSolutionPopup() {
  document.getElementById("solutionPopup").style.display = "none";
}

window.onload = () => {
  setupAlgorithmSelector();
};
window.initMap = initMap;
window.solveCVRP = solveCVRP;
window.closeSolutionPopup = closeSolutionPopup;
window.showSolutionPopup = showSolutionPopup;

