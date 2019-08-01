

function thousands_separators(num) {
  var num_parts = num.toString().split(".");
  num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return num_parts.join(".");
}

function close_movie_data() {
  d3.select("#upcoming-movies").style("display", "block");
  d3.select("#upcoming-text").style("display", "block");
  d3.select("#movie-info").style("display", "none");
}

function movie_data(tmdb_id) {
  d3.select("#upcoming-movies").style("display", "none");
  d3.select("#upcoming-text").style("display", "none");

  // data = sample_movie_data[0];
  d3.json(`/predict/${tmdb_id}`).then(data => {

    d3.select("#poster")
      .html(`<img src='${data.poster_url}' class='card-img-top'>`);

    d3.select("#title-info")
      .html(`
    <h5 id="title" class="card-title">${data.title}</h5>
    <h6 id="tagline" class="card-subtitle mb-2 text-muted">${data.tagline}</h6>
    <p id="summary" class="card-text">${data.overview}</p>`);

    d3.select("#director")
      .html(data.directors.join(", "));

    d3.select("#producer")
      .html(data.producers.join(", "));

    d3.select("#writer")
      .html(data.writers.join(", "));

    d3.select("#budget")
      .html(`$${thousands_separators(data.budget)}`);

    d3.select("#runtime")
      .html(`${data.runtime} min`);

    d3.select("#genres")
      .html(data.genres.join(", "));

    var reldate = new Date(data.release_date);
    console.log(reldate);

    var options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };
    var release_date = reldate.toLocaleDateString("en-US", options);

    d3.select("#release-date")
      .html(release_date);

    d3.select("#prediction")
      .html(() => {
        if (data.predicted_opening > 0) { return `$${thousands_separators(data.predicted_opening)}` }
        else { return "Unknown" }
      });

    d3.select("#movie-info").style("display", "block");
  });
}

function init() {
  d3.json("/upcoming").then(upcoming_data => {
    d3.select("#upcoming-text")
      .html("Current and Upcoming Releases");

    var movies_listed = d3.select("#upcoming-movies")
      .selectAll("div.wrapper-card")
      .data(upcoming_data);
    movies_listed
      .enter()
      .append("div")
      .attr("class", "wrapper-card")
      .html(function (d) {
        return `<div class="card"><a href="#" onclick="movie_data(${d.tmdb_id});" class="stretched-link"></a>
            <img class="card-img-top" src="${d.backdrop_url}" alt="Card image">
            <div class="card-body">
              <h4 class="card-title">${d.title}</h4>
            </div></div><br>`
      });
  });
}

// Initialize the dashboard
init();