import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
from FT_Extractor import FT_Extractor
from environs import env

env.read_env()

POOL_YEARS = [2021, 2022, 2023, 2024, 2025]

def extract_42rio_users(
	logger: logging.Logger, extractor: FT_Extractor, campus_id: int
) -> None:
	for pool_year in range(2021, 2026):
		logger.info(f"Fetching {pool_year} Users Data...")
		users_filters = {"filter[pool_year]": pool_year, "filter[primary_campus_id]": campus_id}
		users_data = extractor.basic_extraction("users", **users_filters)

		logger.info(f"Total users found: {len(users_data)}.")
		logger.info(f"Saving JSON for {pool_year} Users...")
		extractor.set_json(f"piscines_{pool_year}_users", users_data)


def extract_basecamp_projects(
		logger: logging.Logger,
		extractor: FT_Extractor
) -> None:
	projects_data = extractor.filtered_extraction(
		"projects", "cursus/{cursus_id}/projects", {"cursus_id": 51}
	)

	logger.info(f"Saving JSON for the Basecamp Rio Curriculum...")
	logger.info(f"Total projects found: {len(projects_data)}")
	extractor.set_json("basecamp_piscine_projects", projects_data)



if __name__ == "__main__":
	logger = logging.getLogger("42RIO_USERS_EXTRACTION")
	extractor = FT_Extractor()

	logger.info("Fetching Basecamp Rio Curriculum...")
	extract_basecamp_projects(logger, extractor)

	logger.info("Fetching Campus Data...")
	campus = extractor.get_json_data("campus_data")

	logger.info("Fetching Users Data...")
	extract_42rio_users(logger, extractor, campus["id"])
	
	logger.info("In this extraction, we're not getting the projects yet!")
