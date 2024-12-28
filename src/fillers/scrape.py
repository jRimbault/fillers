import os
from concurrent.futures import ThreadPoolExecutor

import requests
import tvdb_v4_official
from bs4 import BeautifulSoup
from pick import pick  # type: ignore

from .show import Show, compress_ranges


def fetch_fillers(show_name: str):
    url = f"https://www.animefillerlist.com/shows/{show_name.replace(' ', '-').lower()}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    filler_episodes: list[int] = []
    for row in soup.select("table tbody tr"):
        cell = row.select_one("td:first-child")
        if cell and "Canon" not in row.text:
            filler_episodes.append(int(cell.text))
    return compress_ranges(filler_episodes)


def fetch_seasons(show_name: str) -> list[int]:
    tvdb = tvdb_v4_official.TVDB(os.environ["TVDB_API_TOKEN"])
    shows = tvdb.search(show_name)  # type: ignore
    options = [f"{s['name']} ({s.get('first_air_time', 'N/A')})" for s in shows]  # type: ignore
    _, i = pick(options, "Pick a show:")  # type: ignore
    show = shows[i]  # type: ignore
    show = tvdb.get_series_extended(show["tvdb_id"])  # type: ignore
    seasons = sorted(  # type: ignore
        (
            tvdb.get_season_extended(s["id"])  # type: ignore
            for s in show["seasons"]  # type: ignore
            if s["type"]["id"] == 1 and s["number"] != 0
        ),
        key=lambda s: s["number"],  # type: ignore
    )
    return [len(s["episodes"]) for s in seasons]  # type: ignore


def look_for(show_name: str):
    with ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(fetch_fillers, show_name)
        seasons = fetch_seasons(show_name)
        fillers = f.result()
    return Show(seasons_episodes=seasons, fillers_compressed=fillers)
