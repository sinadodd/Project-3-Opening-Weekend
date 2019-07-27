var OlympicResults;
var chartGroup;
var runnersGroup;
var toolTip;
var width;
var height;
var margin;
var svgWidth;
var svgHeight;
var runnersList = [];

// clear runnersList when "Clear All" button is clicked
function clearRunnersList() {
  runnersList = [];
  updateSelRunners();
}

// will need to sort the runnersList when running buildPlot3
function compareValues(key, order = 'asc') {
  return function (a, b) {
    if (!a.hasOwnProperty(key) ||
      !b.hasOwnProperty(key)) {
      return 0;
    }

    const varA = (typeof a[key] === 'string') ?
      a[key].toUpperCase() : a[key];
    const varB = (typeof b[key] === 'string') ?
      b[key].toUpperCase() : b[key];

    let comparison = 0;
    if (varA > varB) {
      comparison = 1;
    } else if (varA < varB) {
      comparison = -1;
    }
    return (
      (order == 'desc') ?
        (comparison * -1) : comparison
    );
  };
}

// convert results into seconds
function magic(time) {
  if (typeof time == "number") {
    return time;
  }

  // strip wind factors
  var lastcomma = time.lastIndexOf(",");
  if (lastcomma >= 0) {
    time = time.slice(0, lastcomma)
  }

  var lastcolon = time.lastIndexOf(":");
  var sec = parseFloat(time.slice(lastcolon + 1));
  if (lastcolon < 0) {
    return sec
  }

  time = time.slice(0, lastcolon);

  var min = parseFloat(time.slice(-2));
  if (!isNaN(min)) {
    sec += (min * 60)
  }

  var hrs = parseFloat(time.slice(0, -3));
  if (!isNaN(hrs)) {
    sec += (hrs * 3600)
  }
  return sec;
}

// get distance in m from the event name
function dist(name) {
  var firstspace = name.indexOf(" ");
  name = name.slice(0, firstspace);
  if (name == "Marathon") {
    return 42195
  }
  var distance = parseFloat(name);
  if (name.indexOf("K") > 0) {
    distance *= 1000
  }
  return distance
}

function updateSelRunners() {
  var runnersGroup = d3.select("#selRunners")
    .selectAll("ul")
    .data(runnersList);
  runnersGroup
    .enter()
    .append("ul")
    .merge(runnersGroup)
    .html(function (d) {
      return `<h2><strong>${d.name}</strong> (${d.nationality})<br>${d.year} ${d.event} <strong>(${d.medal})</strong></h2>`;
    });
  runnersGroup.exit().remove();
}

// get flattened array of data to plot
// [{year, location, medal, name, nationality, result, speed}, {}, {}]
function getPlotData(event) {
  var plotData = [];

  var a = OlympicResults.find(e => e.name == event);

  console.log(OlympicResults);
  console.log(event)
  a.games.forEach(g => {
    g.results.forEach(r => {

      plotData.push({
        'event': a.name,
        'distance': a.distance,
        'year': g.year,
        'location': g.location,
        'medal': r.medal,
        'name': r.name,
        'nationality': r.nationality,
        'result': r.result,
        'originalResult': r.originalResult,
        'speed': r.speed
      })
    })
  });
  return plotData;
}

// =====================================================
// ==== BuildPlot1 whenever event is changed ===========
// =====================================================
function buildPlot1(event) {
  var plotData = getPlotData(event);
  console.log(plotData)
  // Create scale functions
  var xLinearScale = d3.scaleLinear()
    .domain([d3.min(plotData, d => d.year) - 3, d3.max(plotData, d => d.year) + 3])
    .range([0, width]);

  var yLinearScale = d3.scaleLinear()
    .domain([d3.min(plotData, d => d.speed), d3.max(plotData, d => d.speed) * 1.01])
    .range([height, 0]);

  // Create axis functions
  var bottomAxis = d3.axisBottom(xLinearScale).tickFormat(d3.format("d"));
  var leftAxis = d3.axisLeft(yLinearScale);

  // Update Axes in Chart
  chartGroup.selectAll(".x_axis")
    .call(bottomAxis);

  chartGroup.selectAll(".y_axis")
    .call(leftAxis);

  // Initialize tool tip
  toolTip.html(function (d) {
    var speed = d3.format('.3f')(d.speed);
    return (`<strong>${d.name}</strong> (${d.nationality})<br>${d.location} ${d.year}<br>Result: ${d.originalResult}<br>Speed: ${speed} m/s<br><a id="select_runner_link" href="#">Select Runner</a>`);
  });

  // Create Circles and Text
  var namesGroup = chartGroup.selectAll(".plot3names").remove();

  var circlesGroup = chartGroup.selectAll(".symbol")
    .data(plotData);
  circlesGroup
    .enter()
    .append("text")
    .attr("class", "symbol fa")
    .on("mouseover", function (data) {
      console.log(this);
      toolTip.show(data, this);
      d3.selectAll("#select_runner_link")
        .on("click", function () {
          runnersList.push(Object.assign({}, data));
          updateSelRunners();
          console.log(runnersList)
        });
    })
    .on("click", function (data) {
      toolTip.hide(data);
    })
    .merge(circlesGroup)
    .attr("x", d => xLinearScale(d.year))
    .attr("y", height)
    .transition()
    .delay(200)
    .duration(500)
    .text("\uf5a2")
    .attr("x", d => xLinearScale(d.year))
    .attr("y", d => yLinearScale(d.speed))
    .attr("opacity", d => {
      if (d.medal == "B") { return "0.6" };
      if (d.medal == "S") { return "0.7" };
      if (d.medal == "G") { return "1" };
      return "1"
    })
    .attr("fill", d => {
      if (d.medal == "B") { return "#A77044" }
      else if (d.medal == "S") { return "#A7A7AD" }
      else if (d.medal == "G") { return "gold" }
      return "black"
    });
  circlesGroup
    .exit()
    // .transition()
    // .duration(200)
    // .attr("y", 0)
    .remove();

  chartGroup.selectAll("rect.lane")
    .remove();

  // Create axes labels
  chartGroup.selectAll("#y_text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .attr("class", "aText")
    .text("Avg Speed (m/s)");

  chartGroup.selectAll("#x_text")
    .attr("transform", `translate(${width / 2}, ${height + margin.top + 30})`)
    .attr("class", "aText")
    .text("Year");
}

// =====================================================
// ==== Call Plot2 when a YEAR has been selected =======
// =====================================================
function buildPlot2(event, year) {
  var plotData = getPlotData(event).filter(d => d.year == year);
  // Add field for distance the non-winners got to when the winner finished
  var minResult = d3.min(plotData, d => d.result);
  plotData.forEach(d => {
    d.runDistance = d.speed * minResult;
    if (d.medal == "G") { d.place = 1 }
    else if (d.medal == "S") { d.place = 2 }
    else if (d.medal == "B") { d.place = 3 }
    else { d.place = 0 };
  });
  console.log(plotData)
  // Create scale functions
  var xLinearScale = d3.scaleLinear()
    .domain([d3.min(plotData, d => d.runDistance) * .999, d3.max(plotData, d => d.runDistance)])
    .range([0, width]);

  var yLinearScale = d3.scaleLinear()
    .domain([3.5, 0.5])
    .range([height, 0]);

  // Create axis functions
  var bottomAxis = d3.axisBottom(xLinearScale).tickFormat(d3.format(""));
  var leftAxis = d3.axisLeft(yLinearScale).tickFormat(d3.format("d")).ticks(plotData.length);

  // Update Axes in Chart
  chartGroup.selectAll(".x_axis")
    .call(bottomAxis);

  chartGroup.selectAll(".y_axis")
    .call(leftAxis);

  // Initialize tool tip
  toolTip.html(function (d) {
    var distance = d3.format('.3f')(d.distance - d.runDistance);
    return (`<strong>${d.name}</strong> (${d.nationality})<br>Result: ${d.originalResult}<br>Distance from Finishline:<br>${distance} m<br><a id="select_runner_link" href="#">Select Runner</a>`);
  });

  // Create Circles and Text
  var namesGroup = chartGroup.selectAll(".plot3names").remove();

  var circlesGroup = chartGroup.selectAll(".symbol")
    .data(plotData);
  circlesGroup
    .enter()
    .append("text")
    .attr("class", "symbol fa")
    .on("mouseover", function (data) {
      console.log(this);
      toolTip.show(data, this);
      d3.selectAll("#select_runner_link")
        .on("click", function () {
          runnersList.push(Object.assign({}, data));
          updateSelRunners();
          console.log(runnersList)
        });
    })
    .on("click", function (data) {
      toolTip.hide(data);
    })
    .merge(circlesGroup)

    .attr("x", 0)
    .attr("y", d => yLinearScale(d.place))
    .transition()
    .delay(200)
    .duration(1500)

    .text("\uf70c")
    .attr("x", d => xLinearScale(d.runDistance))
    .attr("opacity", d => {
      if (d.medal == "G") { return "1" };
      if (d.medal == "S") { return "0.7" };
      if (d.medal == "B") { return "0.6" };
      return "1"
    })
    .attr("fill", d => {
      if (d.medal == "G") { return "gold" }
      else if (d.medal == "S") { return "#A7A7AD" }
      else if (d.medal == "B") { return "#A77044" }
      return "black"
    });

  circlesGroup
    .exit()
    .transition()
    .duration(200)
    .attr("x", width)
    .remove();

  // Create axes labels
  chartGroup.selectAll("#y_text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .attr("class", "aText")
    .text("Place");

  chartGroup.selectAll("#x_text")
    .attr("transform", `translate(${width / 2}, ${height + margin.top + 30})`)
    .attr("class", "aText")
    .text("Distance (m)");
}

// =====================================================
// ==== Plot3 for simulation run =======================
// =====================================================
function buildPlot3(event, year) {
  toolTip.hide();
  runnersList.sort(compareValues('speed', 'desc'));

  runnersList.forEach((d, i) => {
    d.place = i + 1;
  });

  // Create scale functions
  var xLinearScale = d3.scaleLinear()
    .domain([d3.min(runnersList, d => d.speed) * 0.95, d3.max(runnersList, d => d.speed) * 1.07])
    .range([0, width]);

  var yLinearScale = d3.scaleLinear()
    .domain([(runnersList.length + .5), 0.5])
    .range([height, 0]);

  // Create axis functions
  var bottomAxis = d3.axisBottom(xLinearScale);
  var leftAxis = d3.axisLeft(yLinearScale).tickFormat(d3.format("d")).ticks(runnersList.length);

  // Update Axes in Chart
  chartGroup.selectAll(".x_axis")
    .call(bottomAxis);

  chartGroup.selectAll(".y_axis")
    .call(leftAxis);

  // Initialize tool tip
  toolTip.html(function (d) {
    var speed = d3.format('.3f')(d.speed);
    return (`Place: ${d.place}<br><strong>${d.name}</strong> (${d.nationality})<br>${d.year} ${d.event}<br>Speed: ${speed} m/s`);
  });

  // Create Circles and Text
  var circlesGroup = chartGroup.selectAll(".symbol")
    .data(runnersList);
  circlesGroup
    .enter()
    .append("text")
    .attr("class", "symbol fa")
    .on("mouseover", function (data) {
      console.log(this);
      toolTip.show(data, this);
    })
    .on("click", function (data) {
      toolTip.hide(data);
    })
    .merge(circlesGroup)

    .attr("x", 0)
    .attr("y", d => yLinearScale(d.place))
    .transition()
    .delay(200)
    .duration(1500)

    .text(d => `\uf70c`)
    .attr("x", d => xLinearScale(d.speed))
    .attr("y", d => yLinearScale(d.place))
    .attr("opacity", d => {
      if (d.place == "1") { return "1" };
      if (d.place == "2") { return "0.8" };
      if (d.place == "3") { return "0.7" };
      return "0.9"
    })
    .attr("fill", d => {
      if (d.place == "3") { return "#A77044" }
      else if (d.place == "2") { return "#A7A7AD" }
      else if (d.place == "1") { return "gold" }
      return "black"
    });
  circlesGroup
    .exit()
    .transition()
    .duration(200)
    .attr("x", width)
    .remove();

  var namesGroup = chartGroup.selectAll(".plot3names")
    .data(runnersList);
  namesGroup
    .enter()
    .append("text")
    .attr("class", "plot3names")
    .merge(namesGroup)

    .attr("x", 0)
    .attr("y", d => yLinearScale(d.place))
    .attr("transform", "translate(-30, 23)")
    .transition()
    .delay(1350)
    .duration(100)

    .text(d => `${d.name}`)
    .attr("x", d => xLinearScale(d.speed))
    .attr("y", d => yLinearScale(d.place))
    .attr("transform", "translate(-30, 23)")
    .attr("fill", d => {
      if (d.place == "3") { return "#A77044" }
      else if (d.place == "2") { return "#A7A7AD" }
      else if (d.place == "1") { return "gold" }
      return "black"
    });
  namesGroup
    .exit()
    .transition()
    .duration(200)
    .attr("x", width)
    .remove();


  // Create axes labels
  chartGroup.selectAll("#y_text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .attr("class", "aText")
    .text("Place");

  chartGroup.selectAll("#x_text")
    .attr("transform", `translate(${width / 2}, ${height + margin.top + 30})`)
    .attr("class", "aText")
    .text("Speed (m/s)");

};

// init put the svg in the right html id, 
// cleans the data (removes field-type events and called magic function to change results/times to matching format)
// sets eventselector and calls eventChanged
function init() {
  var eventSelector = d3.select("#selEvent");
  runnersGroup = d3.select("#selRunners");

  svgWidth = 800;
  svgHeight = 500;
  margin = {
    top: 6,
    right: 14,
    bottom: 50,
    left: 55
  };

  width = svgWidth - margin.left - margin.right;
  height = svgHeight - margin.top - margin.bottom;

  var svg = d3
    .select("#plot")
    .append("svg")
    // .attr("width", svgWidth)
    // .attr("height", svgHeight)
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", `0 0 ${svgWidth} ${svgHeight}`)
    .classed("svg-content", true);
  ;

  chartGroup = svg.append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`)
    ;

  var xLinearScale = d3.scaleLinear()
    .domain([0, 1])
    .range([0, width]);

  var yLinearScale = d3.scaleLinear()
    .domain([0, 1])
    .range([height, 0]);

  // Create axis functions
  var bottomAxis = d3.axisBottom(xLinearScale);
  var leftAxis = d3.axisLeft(yLinearScale);


  // Append Axes to the chart
  chartGroup.append("g")
    .attr("transform", `translate(0, ${height})`)
    .attr("class", "x_axis")
    .call(bottomAxis);

  chartGroup.append("text")
    .attr("id", "x_text");

  chartGroup.append("g")
    .attr("class", "y_axis")
    .call(leftAxis);

  chartGroup.append("text")
    .attr("id", "y_text");

  toolTip = d3.tip()
    .attr("class", "d3-tip")
    .offset([0, 0]);
  chartGroup.call(toolTip);

  var exclusions = ["Relay", "Shot", "Pole", "Jump", "Throw", "Decathlon", "Heptathlon"];

  d3.json("data/results.json").then((data) => {
    OlympicResults = data

      // remove events that are in my "exclusions" list
      .filter(event => !exclusions.find(n => event.name.includes(n)))

      // add a distance field, remove where results is NONE, change time to seconds, add speed field (m/s)
      .map(event => {
        event.distance = dist(event.name);
        event.games = event.games.map(game => {
          game.results = game.results
            .filter(result => result.result)
            .map(result => {
              result.originalResult = result.result;
              result.result = magic(result.result);
              result.speed = event.distance / result.result;
              return result
            })
          return game
        })
        return event
      });

    console.log(OlympicResults);

    OlympicResults.forEach((o) => {
      eventSelector
        .append("option")
        .text(o.name)
        .property("value", o.name);
    });

    const firstEvent = data[0];

    eventChanged(firstEvent.name);
  });
}

// changes what options appear in the yearSelector when the event is changed.
// calls yearChanged
function eventChanged(newEvent) {
  var yearSelector = d3.select("#selYear");
  yearSelector.html('<option value="all">all</option>');
  d3.json("data/results.json").then((data) => {
    data
      .find((o) => o.name == newEvent)
      .games
      .map(g => g.year)
      .sort((a, b) => a - b)
      .forEach((year) => {
        yearSelector
          .append("option")
          .text(year)
          .property("value", year);
      });

    yearChanged('all');
  });
}

function yearChanged(year) {
  toolTip.hide();
  var event = d3.select("#selEvent").node().value;
  console.log(event);
  if (year == 'all') {
    buildPlot1(event)
  }
  else {
    buildPlot2(event, year)
  }
}

init();
