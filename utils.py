import requests

def get_all_cursus(access_token: str) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get("https://api.intra.42.fr/v2/cursus", headers=headers)
    response.raise_for_status()
    return response.json()

def get_all_students_by_cursus(access_token: str, cursus_id: int, campus_id: int, user_id: int) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "filter[cursus_id]": cursus_id,
        "page[size]": 1000,
        "filter[campus_id]": campus_id,
        "filter[user_id]": user_id
    }
    
    response = requests.get(f"https://api.intra.42.fr/v2/cursus_users", headers=headers, params=params)
    response.raise_for_status()
    with open('students.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    return response.json()

def get_users_me(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
    response.raise_for_status()
    return response.json()

def get_campus_users(access_token: str, user_id: int) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "page[size]": 1000,
        "filter[user_id]": user_id
    }
    
    response = requests.get(f"https://api.intra.42.fr/v2/campus_users", headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_projects_by_user(access_token: str, user_id: int) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "filter[user_id]": user_id,
        "page[size]": 1000
    }
    
    response = requests.get("https://api.intra.42.fr/v2/projects_users", headers=headers, params=params)
    response.raise_for_status()
    return response.json()