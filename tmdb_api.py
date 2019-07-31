import json
import re
import time
import traceback
from typing import List, Optional, Dict

import tmdbsimple as tmdb
from requests import HTTPError, Response

import config

tmdb.API_KEY = config.api_key

DIRECTOR_JOBS = ['Director']
PRODUCER_JOBS = ['Producer', 'Executive Producer', 'Co-Producer', 'Co-Executive Producer']
WRITER_JOBS = ['Writer', 'Co-Writer', 'Screenplay', 'Story', 'Adaptation', 'Author', 'Comic Book', 'Novel',
               'Original Story']


class InputSample:

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

    def to_json(self):
        return self.__dict__.copy()

    tmdb_id: int
    actual_opening: int = None
    predicted_opening: float = None

    poster_url: str = None
    backdrop_url: str = None
    tagline: str = None
    release_date: str = None
    title: str = None
    overview: str = None

    # Features:
    # theaters: number of theaters released to
    # theaters: int = None
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
    # studio: name of production companies
    studios: List[str] = None
    # rating: MPAA picture rating
    rating: str = None
    # month: month of release 1-12
    month: int = None
    # day: day of month of release 1-31
    day: int = None
    # keywords
    keywords: List[str] = None


def load_from_tmdb(tmdb_id: int) -> (Optional[InputSample], Optional[str], str):
    movie = tmdb.Movies(tmdb_id)
    movie_data = movie.info(append_to_response="releases,credits,keywords")
    return parse_json(tmdb_id, movie_data) + (json.dumps(movie_data),)


def parse_json(tmdb_id: int, movie_data: Dict) -> (Optional[InputSample], Optional[str]):
    err = []
    ret = InputSample(tmdb_id=tmdb_id)

    ret.poster_url = f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}" if 'poster_path' in movie_data else None
    ret.backdrop_url = f"https://image.tmdb.org/t/p/original{movie_data['backdrop_path']}" if 'backdrop_path' in movie_data else None

    ret.release_date = movie_data['release_date']
    ret.title = movie_data['title']
    ret.overview = movie_data['overview']

    if 'runtime' in movie_data:
        ret.runtime = movie_data['runtime']

    if 'budget' in movie_data:
        ret.budget = movie_data['budget']

    if 'genres' in movie_data:
        ret.genres = [g['name'] for g in movie_data['genres']]

    if 'tagline' in movie_data:
        ret.tagline = movie_data['tagline']

    if 'keywords' in movie_data:
        ret.keywords = [k['name'] for k in movie_data['keywords']['keywords']]

    if 'releases' in movie_data:
        for c in movie_data['releases']['countries']:
            if c['iso_3166_1'] == 'US':
                ret.rating = c['certification']
                (_, month, day) = c['release_date'].split("-")
                ret.month = int(month)
                ret.day = int(day)
                break
        else:
            err += [f"No US release for TMDB ID {tmdb_id}"]

    if 'production_companies' in movie_data:
        ret.studios = [c['name'] for c in movie_data['production_companies']]

    if 'credits' in movie_data:
        ret.directors = [c['name'] for c in movie_data['credits']['crew']
                         if c['department'] == 'Directing' and c['job'] in DIRECTOR_JOBS]
        ret.producers = [c['name'] for c in movie_data['credits']['crew']
                         if c['department'] == 'Production' and c['job'] in PRODUCER_JOBS]
        ret.writers = [c['name'] for c in movie_data['credits']['crew']
                       if c['department'] == 'Writing' and c['job'] in WRITER_JOBS]

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


def load_tmdb_data_by_title(title: str, year: int = None) -> (InputSample, Optional[str], str):
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
            return InputSample(0), str(e), None


def get_upcoming() -> List[InputSample]:
    resp = tmdb.Movies().upcoming(language="en-US")
    return [parse_json(r['id'], r)[0] for r in resp['results']]


if __name__ == "__main__":
    get_tmdb_id_from_title("The Lion King (2019)")
    get_tmdb_id_from_title("Aliens (1986)")

