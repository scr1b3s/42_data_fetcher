"""
Scripts used to facilitate all kinds of processes, such as fetching data from École 42 API, or managing pagination and wait time.
"""

import requests
import time
import re

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
    """
    Fetches the number of pages on a given resource, taking into account the number of rows requested in the param.

    Args:
        access_token: The Bearer credential that's going to be sent w/ the Authorization Header.
        request_url: The URL for the request we're going to make... Probably a GET type.
        params: Requests' params that's going to be used in the arguments.

    Returns:
        last_page: The last page, as a integer, corresponding to the total amount of pages needed to be transversed.
    """
    logger = logging.getLogger(__name__)
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(request_url, headers=headers, params=params)
    response.raise_for_status()

    last_page = None

    link_header = response.headers.get("Link")
    if link_header:
        match = re.search(r'page=(\d+)&per_page=\d+>; rel="last"', link_header)
        if match:
            last_page = int(match.group(1))
            logger.info(f"I've found {last_page} pages!")
        else:
            logger.info("No pages, just the one.")
    else:
        logger.warning("No Link header, assuming only one page.")

    wait()

    return last_page


def get_all_cursus(
    access_token: str,
    per_page: int = 100
) -> list:
    """
    Makes a series of requests to École 42's API using gets_pages to determine the last page, with the objetive of transversing all cursus' data.

    Args:
        access_token: Access token to be used in Authorization Header.
        per_page: Number of lines to format the data, defaults to 100, the maximum number of lines.
    
    Returns:
        A list of dictionaries corresponding to the cursus data for all the cursus from 42.
    """
    logger = logging.getLogger(__name__)
    headers = {"Authorization": f"Bearer {access_token}"}

    start_page = 1

    params = {
        "page": {
            "number": start_page,
        },
        "per_page": per_page,
    }

    last_page = gets_pages(access_token, "https://api.intra.42.fr/v2/cursus", params)
    total_pages = last_page if last_page else 1

    total_data = []

    if start_page == total_pages:
        logger.info(f"Extracting data from Cursus.")
        response = requests.get("https://api.intra.42.fr/v2/cursus", headers=headers)
        response.raise_for_status()
        total_data.append(response.json())

    else:
        while params["page"]["number"] < total_pages:
            logger.info(f"Extracting data from Cursus, page {params['page']['number']}.")
            response = requests.get(
                "https://api.intra.42.fr/v2/cursus", headers=headers
            )
            response.raise_for_status()
            total_data.append(response.json())
            params["page"]["number"] += 1
            wait()

    flat_data = [item for sublist in total_data for item in sublist]
    return flat_data


def get_campus(
    access_token: str,
    city_filter: str,
) -> dict:
    """
    Makes a request to the École 42 API to get 42 Rio's campus data.

    Args:
        access_token: Access token to be used in the Authorization Header.
    
    Returns:
        A dictionary corresponding to Rio's campus data.    
    """
    logger = logging.getLogger(__name__)
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        'filter[city]': city_filter
    }

    logger.info(f"Extracting {city_filter} Campus Data...")
    response = requests.get(
        f"https://api.intra.42.fr/v2/campus", headers=headers, params=params
    )

    response.raise_for_status()
    response = response.json()
    response = response[0]

    return response

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
