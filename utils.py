"""
Scripts used to facilitate all kinds of processes, such as fetching data from École 42 API, or managing pagination and wait time.
"""

import requests
import time
import re


def wait() -> None:
    """
    Waits a second.

    Since the API has a wait period, every request we make needs to wait a little. It would get tedious real quick to type "sleep" or "time.sleep(1)"
    """
    time.sleep(1)


def gets_pages(
    access_token: str,
    request_url: str,
    params: dict,
) -> int | None:
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(request_url, headers=headers, params=params)
    response.raise_for_status()

    last_page = None

    link_header = response.headers["Link"]
    match = re.search(r'page=(\d+)&per_page=\d+>; rel="last"', link_header)

    if match:
        last_page = int(match.group(1))
        print(f"I've found {last_page} pages!")
    else:
        print("No pages, just the one.")
    
    wait()

    return last_page


def get_all_cursus(access_token: str) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get("https://api.intra.42.fr/v2/cursus", headers=headers)
    response.raise_for_status()
    return response.json()


def get_all_students_by_cursus(
    access_token: str, cursus_id: int, campus_id: int, user_id: int
) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "filter[cursus_id]": cursus_id,
        "page[size]": 1000,
        "filter[campus_id]": campus_id,
        "filter[user_id]": user_id,
    }

    response = requests.get(
        f"https://api.intra.42.fr/v2/cursus_users", headers=headers, params=params
    )
    response.raise_for_status()
    with open("students.json", "w", encoding="utf-8") as f:
        import json

        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    return response.json()


def get_users_me(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
    response.raise_for_status()
    return response.json()


def get_campus_users(access_token: str, user_id: int) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"page[size]": 1000, "filter[user_id]": user_id}

    response = requests.get(
        f"https://api.intra.42.fr/v2/campus_users", headers=headers, params=params
    )
    response.raise_for_status()
    return response.json()


def get_projects_by_user(access_token: str, user_id: int) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"filter[user_id]": user_id, "page[size]": 1000}

    response = requests.get(
        "https://api.intra.42.fr/v2/projects_users", headers=headers, params=params
    )
    response.raise_for_status()
    return response.json()
