// Set up map dimensions and projection
const width = 960;
const height = 500;
const svg = d3.select("#map").append("svg")
    .attr("width", width)
    .attr("height", height);

console.log("SVG element created");

// Load map boundaries (GeoJSON) and temperature data for city-level
Promise.all([
    d3.json("/static/world.geojson"),  // Local GeoJSON file
]).then(([geoData]) => {
    const projection = d3.geoNaturalEarth1()
        .scale(150)
        .translate([width / 2, height / 2]);

    const path = d3.geoPath().projection(projection);

    svg.append("g")
        .selectAll("path")
        .data(geoData.features)
        .join("path")
        .attr("fill", "#ccc")
        .attr("d", path)
        .attr("stroke", "black");

    console.log("Map boundaries rendered");

    // Set up color scale for temperatures
    const colorScale = d3.scaleSequential(d3.interpolatePlasma)
        .domain([0, 40]);  // Adjusted to [0, 40] for common temperature ranges

    // Function to update map with temperature data for the selected year
    function updateMap(year) {
        console.log(`Fetching data for year ${year}`);

        // Fetch city-level data for the specified year
        d3.json(`/data?year=${year}`).then(yearData => {
            if (yearData.error) {
                console.error(yearData.error);
                return;
            }

            console.log(`Data for year ${year}:`, yearData);

            // Remove any existing circles
            svg.selectAll("circle").remove();

            // Check if there is data for the selected year
            if (!yearData || yearData.length === 0) {
                console.warn("No data available for the selected year.");
                return;
            }

            // Bind data and create circles for each temperature data point
            svg.selectAll("circle")
                .data(yearData)
                .join("circle")
                .attr("cx", d => projection([d.longitude, d.latitude])[0])
                .attr("cy", d => projection([d.longitude, d.latitude])[1])
                .attr("r", 4)
                .attr("fill", d => colorScale(d.averagetemperature))
                .attr("opacity", 0.75)
                .append("title")
                .text(d => `${d.city}, ${d.country}: ${d.averagetemperature.toFixed(1)}°C`);

            console.log("City-level temperature data points rendered for year", year);
        }).catch(error => console.error("Error fetching data:", error));
    }

    // Initialize with the first year in the slider range
    updateMap(1850);

    // Update map when the slider changes
    d3.select("#yearSlider").on("input", function() {
        const year = +this.value;
        d3.select("#yearDisplay").text(year);
        updateMap(year);
    });
});
