import requests

def get_acess_token(client_id: str, client_secret: str, token_url: str) -> str:
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)

    response.raise_for_status()

    data = response.json()
    return data["access_token"]

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

def get_users_for_campus(access_token, campus_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(f"https://api.intra.42.fr/v2/campus/{campus_id}/users", headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    token = get_acess_token(
        CLIENT_ID,
        CLIENT_SECRET,
        TOKEN_URL
    )

    # data = get_campus_list_by_country(token, "Brazil")

    # with open('brazil_campuses.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    
    users = get_users_for_campus(token, 28)
    print(users)