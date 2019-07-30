import re
import time
import traceback
from typing import List, Optional

import tmdbsimple as tmdb
from requests import HTTPError, Response

import config

tmdb.API_KEY = config.api_key


class InputSample:

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

    tmdb_id: int
    poster_url: str = None

    # Features:
    # theaters: number of theaters released to
    theaters: int = None
    # budget: movie budget in USD
    budget: int = None
    # runtime: movie run length in minutes
    runtime: float = None
    # genre: array of genre tags
    genres: List[str] = None
    # director: array of director names
    directors: List[str] = None
    # producer: array of producer names
    producers: List[str] = None
    # writer: array of writer names
    writers: List[str] = None
    # studio: name of studio
    studio: str = None
    # rating: MPAA picture rating
    rating: str = None
    # month: month of release 1-12
    month: int = None
    # day: day of month of release 1-31
    day: int = None


def load_from_tmdb(tmdb_id: int) -> (Optional[InputSample], Optional[str]):
    err = []
    movie = tmdb.Movies(tmdb_id)
    ret = InputSample(tmdb_id=tmdb_id)

    movie.info()
    ret.budget = movie.budget
    ret.runtime = movie.runtime
    ret.genres = [g['name'] for g in movie.genres]
    ret.studio = 'BV'  # TODO
    ret.theaters = 0  # TODO

    movie.releases()
    for c in movie.countries:
        if c['iso_3166_1'] == 'US':
            ret.rating = c['certification']
            (_, month, day) = c['release_date'].split("-")
            ret.month = int(month)
            ret.day = int(day)
            break
    else:
        err += [f"No US release for TMDB ID {tmdb_id}"]

    movie.credits()
    ret.directors = [c['name'] for c in movie.crew if c['department'] == 'Directing']
    ret.producers = [c['name'] for c in movie.crew if c['department'] == 'Production']
    ret.writers = [c['name'] for c in movie.crew if c['department'] == 'Writing']

    return ret, ("; ".join(err) or None)


def get_tmdb_id_from_title(title: str, year: int = None) -> Optional[int]:
    y = year
    t = str(title)
    m = re.match(r"^(.*) \((\d{4})\)$", t)
    if m:
        (t, year) = m.groups()
    try:
        r = tmdb.Search().movie(query=t, language="en-US", primary_release_year=y)
    except Exception as e:
        print(f"Got exception for '{title}': {t}, {year}, year: {e}")
        traceback.print_exc()
        raise e

    if not r['total_results']:
        r = tmdb.Search().movie(query=t, langauge="en-US")
        if r['total_results']:
            print(f"{title} / {y} - found {r['total_results']} results without primary_release_year")
        else:
            raise RuntimeError(f"No results returned for '{title}'")

    if r['total_results'] == 1:
        res = r['results'][0]
        if res['title'] != title or res['release_date'][0:4] != str(year):
            print(f"{title} / {year} --> {res['title']} / {res['release_date']}")
        return r['results'][0]['id']

    exact_title_matches = [res for res in r['results'] if res['title'] == t]

    if len(exact_title_matches) > 1 and year:
        exact_title_matches = [res for res in exact_title_matches if res['release_date'][0:4] == str(year)]

    if len(exact_title_matches) > 1:
        print(f"Too many matches for '{title}':")
        for res in exact_title_matches:
            print(f"  - {res['id']} {res['title']} - {res['release_date']}: {res['overview']}")
        # Choose the first result and hope for the best
        print("Choosing the first result...")

    if len(exact_title_matches) == 0:
        print(f"{r['total_results']} matches for '{title}':")
        for res in r['results']:
            print(f"  - {res['id']} {res['title']} - {res['release_date']}: {res['overview']}")
        print("Taking first result...")
        exact_title_matches = r['results']

    return exact_title_matches[0]['id']


def load_tmdb_data_by_title(title: str, year: int = None) -> (InputSample, Optional[str]):
    while True:
        try:
            tmdb_id = get_tmdb_id_from_title(title, year)
            return load_from_tmdb(tmdb_id)
        except HTTPError as e:
            if e.response.status_code == 429:
                response: Response = e.response
                wait = int(response.headers.get("Retry-After")) + 1
                print(f"Got HTTP 429; retrying in {wait} seconds...")
                time.sleep(wait)
            # Retry
        except Exception as e:
            traceback.print_exc()
            # Don't retry
            return InputSample(0), str(e)


if __name__ == "__main__":
    get_tmdb_id_from_title("The Lion King (2019)")
    get_tmdb_id_from_title("Aliens (1986)")

