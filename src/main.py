import requests
from environs import env
import json

env.read_env()

CLIENT_ID = env.str("CLIENT_ID")
CLIENT_SECRET = env.str("CLIENT_SECRET")
TOKEN_URL = env.str("TOKEN_URL")

def get_campus_list_by_country(access_token, country_name):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "filter[country]": country_name
    }
    response = requests.get("https://api.intra.42.fr/v2/campus", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_users_for_campus(access_token, campus_id, per_page=100):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    page = 1
    all_results = []

    params = {
        "page": {
            "number": page
        },
        "per_page": per_page
    }

    response = requests.get(f"https://api.intra.42.fr/v2/campus/{campus_id}/users", headers=headers, params=params)
    response.raise_for_status()

    link_header = response.headers["Link"]
    match = re.search(r'page=(\d+)&per_page=\d+>; rel="last"', link_header)

    if match:
        last_page = int(match.group(1))
        print(last_page)
    else:
        print("No last page. Fuck it.")

    return dict(response.headers)

if __name__ == '__main__':
    token = get_acess_token(
        CLIENT_ID,
        CLIENT_SECRET,
        TOKEN_URL
    )

    # data = get_campus_list_by_country(token, "Brazil")

    data = get_users_for_campus(token, 28)

    with open('users_rio.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    # users = get_users_for_campus(token, 28)
    # print(users)