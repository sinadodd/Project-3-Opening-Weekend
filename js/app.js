
var sample_movie_data = [{
  budget: 55000000,
  genres: ["Drama", "Comedy"],
  overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
  poster_path: "/adw6Lq9FiC9zjYEpOqfq03ituwp.jpg",
  release_date: "1999-10-15",
  runtime: 139,
  tagline: "Mischief. Mayhem. Soap.",
  title: "Fight Club",
  director: ["Bob Smith", "John Doe"],
  producer: ["Bob Smith", "John Doe"],
  writer: ["Bob Smith", "John Doe"],
  predicted_opening: 12000000
},
{
  budget: 63000000,
  genres: ["Drama", "Action", "Comedy"],
  overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
  poster_path: "/adw6Lq9FiC9zjYEpOqfq03ituwp.jpg",
  release_date: "1999-10-15",
  runtime: 139,
  tagline: "Mischief. Mayhem. Soap.",
  title: "Fight Club",
  director: "David Fincher",
  producer: ["Bob Smith", "John Doe"],
  writer: "Jim Uhls"
},
{
  budget: 63000000,
  genres: ["Drama", "Action", "Comedy"],
  overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
  poster_path: "/adw6Lq9FiC9zjYEpOqfq03ituwp.jpg",
  release_date: "1999-10-15",
  runtime: 139,
  tagline: "Mischief. Mayhem. Soap.",
  title: "Fight Club",
  director: "David Fincher",
  producer: ["Bob Smith", "John Doe"],
  writer: "Jim Uhls"
},
{
  budget: 63000000,
  genres: ["Drama", "Action", "Comedy"],
  overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
  poster_path: "/adw6Lq9FiC9zjYEpOqfq03ituwp.jpg",
  release_date: "1999-10-15",
  runtime: 139,
  tagline: "Mischief. Mayhem. Soap.",
  title: "Fight Club",
  director: "David Fincher",
  producer: ["Bob Smith", "John Doe"],
  writer: "Jim Uhls"
},
{
  budget: 63000000,
  genres: ["Drama", "Action", "Comedy"],
  overview: "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
  poster_path: "/adw6Lq9FiC9zjYEpOqfq03ituwp.jpg",
  release_date: "1999-10-15",
  runtime: 139,
  tagline: "Mischief. Mayhem. Soap.",
  title: "Fight Club",
  director: "David Fincher",
  producer: ["Bob Smith", "John Doe"],
  writer: "Jim Uhls"
}
];

var upcoming_data = [{
  "backdrop_url": "https://image.tmdb.org/t/p/original/1TUg5pO1VZ4B0Q1amk3OlXvlpXV.jpg",
  "poster_url": "https://image.tmdb.org/t/p/original/dzBtMocZuJbjLOXvrl4zGYigDzh.jpg",
  "release_date": "2019-07-12", "title": "The Lion King", "tmdb_id": 420818
},
{
  "backdrop_url": "https://image.tmdb.org/t/p/original/b82nVVhYNRgtsTFV1jkdDwe6LJZ.jpg",
  "poster_url": "https://image.tmdb.org/t/p/original/8j58iEBw9pOXFD2L0nt0ZXeHviB.jpg", 
  "release_date": "2019-07-25", "title": "Once Upon a Time in Hollywood", "tmdb_id": 466272
}, 
{ "backdrop_url": "https://image.tmdb.org/t/p/original/fgPZgeqxDKIw86pBiAyLhh0vTrU.jpg", 
"poster_url": "https://image.tmdb.org/t/p/original/keym7MPn1icW1wWfzMnW3HeuzWU.jpg", 
"release_date": "2019-08-01", "title": "Fast & Furious Presents: Hobbs & Shaw", "tmdb_id": 384018 
}, { "backdrop_url": "https://image.tmdb.org/t/p/original/nDP33LmQwNsnPv29GQazz59HjJI.jpg", "poster_url": "https://image.tmdb.org/t/p/original/wgQ7APnFpf1TuviKHXeEe3KnsTV.jpg", "release_date": "2019-05-03", "title": "Pok\u00e9mon Detective Pikachu", "tmdb_id": 447404 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/m67smI1IIMmYzCl9axvKNULVKLr.jpg", "poster_url": "https://image.tmdb.org/t/p/original/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg", "release_date": "2019-06-19", "title": "Toy Story 4", "tmdb_id": 301528 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/2cAce3oD0Hh7f5XxuXmNXa1WiuZ.jpg", "poster_url": "https://image.tmdb.org/t/p/original/mKxpYRIrCZLxZjNqpocJ2RdQW8v.jpg", "release_date": "2019-07-11", "title": "Crawl", "tmdb_id": 511987 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/997ToEZvF2Obp9zNZbY5ELVnmrW.jpg", "poster_url": "https://image.tmdb.org/t/p/original/u3B2YKUjWABcxXZ6Nm9h10hLUbh.jpg", "release_date": "2019-04-11", "title": "After", "tmdb_id": 537915 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/reU8qaO848nkCay7WPtJcdi61p5.jpg", "poster_url": "https://image.tmdb.org/t/p/original/eycO6M2s38xO1888Gq2gSrXf0A6.jpg", "release_date": "2019-07-03", "title": "Midsommar", "tmdb_id": 530385 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/4MDYpCwqSVO5RcTiZ4GEfePzDdl.jpg", "poster_url": "https://image.tmdb.org/t/p/original/9Z2qT9iZYLzzsCSYu7A4SEQsKX0.jpg", "release_date": "2019-07-31", "title": "The Divine Fury", "tmdb_id": 571627 }, { "backdrop_url": "https://image.tmdb.org/t/p/originalNone", "poster_url": "https://image.tmdb.org/t/p/original/olsjvffjYYvhqj3KWaQmD4jNNKp.jpg", "release_date": "2019-07-30", "title": "Illuminated: The True Story of the Illuminati", "tmdb_id": 616800 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/etaok7q2E5tV36oXe7GQzhUQ4fX.jpg", "poster_url": "https://image.tmdb.org/t/p/original/q3mKnSkzp1doIsCye6ap4KIUAbu.jpg", "release_date": "2019-05-24", "title": "The Secret Life of Pets 2", "tmdb_id": 412117 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/t9xAqZc37OgVkojyQwT3UCanZJk.jpg", "poster_url": "https://image.tmdb.org/t/p/original/1rjaRIAqFPQNnMtqSMLtg0VEABi.jpg", "release_date": "2019-06-27", "title": "Yesterday", "tmdb_id": 515195 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/xgfn98c2UzvFWP6MXDzytearmQ3.jpg", "poster_url": "https://image.tmdb.org/t/p/original/7RTaeiHvc9oPfvRMQGUra7qLOQh.jpg", "release_date": "2019-07-11", "title": "Stuber", "tmdb_id": 513045 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/vHse4QK31Vc3X7BKKU5GOQhYxv6.jpg", "poster_url": "https://image.tmdb.org/t/p/original/rpS7ROczWulqfaXG2klYapULXKm.jpg", "release_date": "2019-06-19", "title": "Child's Play", "tmdb_id": 533642 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/k7sE3loFwuU2mqf7FbZBeE3rjBa.jpg", "poster_url": "https://image.tmdb.org/t/p/original/hdYTrfRKrzdbZ3DE72YxmeB0RNg.jpg", "release_date": "2019-08-02", "title": "The Angry Birds Movie 2", "tmdb_id": 454640 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/cxM5ifGuXvuqYM7B0cgrLw08F4R.jpg", "poster_url": "https://image.tmdb.org/t/p/original/qii87VWcs4MRuMs5cGopkEwlLzo.jpg", "release_date": "2019-07-31", "title": "Exit", "tmdb_id": 572164 }, { "backdrop_url": "https://image.tmdb.org/t/p/originalNone", "poster_url": "https://image.tmdb.org/t/p/original/pFcK2DaF2bBUuv5FZjOhzg8jKCC.jpg", "release_date": "2019-08-01", "title": "Jakarta VS Everybody", "tmdb_id": 551478 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/ny5aCtglk2kceGAuAdiyqbhBBAf.jpg", "poster_url": "https://image.tmdb.org/t/p/original/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "release_date": "2019-05-30", "title": "Parasite", "tmdb_id": 496243 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/mYKP6qcDUimVMAHQWLOuDHjO19S.jpg", "poster_url": "https://image.tmdb.org/t/p/original/cVhe15rJLRjolunSWLBN6xQLyGU.jpg", "release_date": "2019-02-14", "title": "Fighting with My Family", "tmdb_id": 445629 }, { "backdrop_url": "https://image.tmdb.org/t/p/original/kmPnDn9mbjD9Vzn1FTclNiSHGNa.jpg", "poster_url": "https://image.tmdb.org/t/p/original/eItrj5GcjvCI3oD3bIcz1A2IL9t.jpg", "release_date": "2019-06-07", "title": "I Am Mother", "tmdb_id": 505948 }];

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
  d3.select("#movie-info").style("display", "block");

  data = sample_movie_data[0];
  // d3.json(`/info/${tmdb_id}`).then(data => {

  d3.select("#poster")
    .html(`<img src='https://image.tmdb.org/t/p/original${data.poster_path}' class='card-img-top'>`)

  d3.select("#title-info")
    .html(`
    <h5 id="title" class="card-title">${data.title}</h5>
    <h6 id="tagline" class="card-subtitle mb-2 text-muted">${data.tagline}</h6>
    <p id="summary" class="card-text">${data.overview}</p>`)

  d3.select("#director")
    .html(data.director.join(", "))

  d3.select("#producer")
    .html(data.producer.join(", "))

  d3.select("#writer")
    .html(data.writer.join(", "))

  d3.select("#budget")
    .html(`$${thousands_separators(data.budget)}`)

  d3.select("#runtime")
    .html(`${data.runtime} min`)

  d3.select("#genres")
    .html(data.genres.join(", "))

  var reldate = new Date(data.release_date)
  console.log(reldate);

  var options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };
  var release_date = reldate.toLocaleDateString("en-US", options);

  d3.select("#release-date")
    .html(release_date)

  d3.select("#prediction")
    .html(`$${thousands_separators(data.predicted_opening)}`)
  // });
}

function init() {
  d3.select("#upcoming-text")
    .html("Upcoming Releases");

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
}

// Initialize the dashboard
init();