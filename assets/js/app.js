let cartogephi = undefined;
let search = undefined;
let marker = undefined;
let map = undefined;

document.addEventListener('readystatechange', event => {
  switch (document.readyState) {
    case "complete":
      load_cartogephi();
      break;
  }
});

function load_cartogephi() {
  let r = Math.random();
  fetch(`./cartogephi.json?{r}`) 
      .then((response) => response.json())
      .then((json) => {
            cartogephi = json;
            map = L.map('map', {
                crs: L.CRS.Simple,
                minZoom: -5
            });
            L.imageOverlay(cartogephi.img_file, cartogephi.leaflet_config).addTo(map);
            map.fitBounds(cartogephi.leaflet_config);
            const layerControl = L.control.layers().addTo(map);
            for(let mid in cartogephi.modularities) {
                const modularity = cartogephi.modularities[mid];
                const [r,g,b] = modularity['color'];
                const layer = L.layerGroup();
                layerControl.addOverlay(layer,`${mid}`)
                L.polygon(modularity['hull']).setStyle({
                    fillColor: `rgb(${r},${g},${b})`,
                    color:  `rgb(${r},${g},${b})`
                }).bindPopup(`${mid}`).addTo(layer)
            }
      });

  search = document.getElementById("searchInput");
  search.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      const find = cartogephi.index[search.value];
      if(find !== undefined){
        if(marker !== undefined) {
           map.removeLayer(marker)
        }
        var sol = L.latLng([find.y, find.x]);
        map.panTo(sol);
        (marker=L.marker(sol)).addTo(map);
        marker.bindPopup(`<h2>${find['label']}</h2>`).openPopup()
      }
    }
  });
}