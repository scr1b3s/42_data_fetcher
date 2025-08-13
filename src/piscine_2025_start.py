import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
from FT_Extractor import FT_Extractor
from environs import env

env.read_env()

def extract_c_piscine_curriculum(
        logger: logging.Logger,
        extractor: FT_Extractor
) -> None:
    projects_data = extractor.filtered_extraction(
        "projects", "cursus/{cursus_id}/projects", {"cursus_id": 9}
    )

    logger.info(f"Saving JSON for C Piscine Curriculum...")
    logger.info(f"Total projects found: {len(projects_data)}")
    extractor.set_json("c_piscine_projects", projects_data)

def extract_piscine_2025_users(
    logger: logging.Logger, extractor: FT_Extractor, campus_id: int
) -> None:
    users_filters = {"filter[pool_year]": 2025, "filter[pool_month]": "september,august", "filter[primary_campus_id]": campus_id}
    users_data = extractor.basic_extraction("users", **users_filters)

    logger.info(f"Total users found: {len(users_data)}.")
    logger.info("Saving JSON for Users...")
    extractor.set_json("piscine_2025_users", users_data)


def extract_piscine_2025_projects_init(
    logger: logging.Logger, extractor: FT_Extractor, campus_id: int, user_data: dict
) -> None:
    projects_filters = {"cursus": 9, "campus": campus_id}
    projects_data = []

    for user in user_data:
        instance_data = extractor.filtered_extraction(
            "projects",
            "users/{user_id}/projects_users",
            {"user_id": user["id"]},
            **projects_filters
        )

        projects_data.append(instance_data)
    
    all_items = []
    for data in projects_data:
        all_items.extend(data)

    logger.info("Saving JSON for Initial Projects...")
    extractor.set_json("piscine_2025_projects_init", all_items)


if __name__ == "__main__":
    logger = logging.getLogger("INITIAL_EXTRACTION")
    extractor = FT_Extractor()

    logger.info("Fetching C Piscine Curriculum...")
    extract_c_piscine_curriculum(logger, extractor)

    logger.info("Fetching Campus Data...")
    campus = extractor.get_json_data("campus_data")

    extract_piscine_2025_users(logger, extractor, campus["id"])

    logger.info("Fetching Users Data...")
    users_data = extractor.get_json_data("piscine_2025_users")

    extract_piscine_2025_projects_init(logger, extractor, campus['id'], users_data)
