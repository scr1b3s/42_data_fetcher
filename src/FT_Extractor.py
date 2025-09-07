import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
import requests
import time
import json
from FT_Client import FT_Client
from environs import env

logging.basicConfig(
	level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

DATA_DIR = "data"

class FT_Extractor(FT_Client):
	def __init__(self):
		env.read_env()	
		super().__init__()

		self._base_url = env.str("REQ_URL")
		self._extractor_logger = logging.getLogger("FT_Extractor")
		self._extractor_logger.info("Initializing FT_Extractor...")

	def get_pages(
		self,
		endpoint: str,
		params: dict,
	) -> int:
		logger = self._extractor_logger
		headers = {"Authorization": f"Bearer {self.token}"}
		request_url = f"{self._base_url}{endpoint}"

		logger.info(f"Checking pages for: {endpoint}...")

		response = requests.get(request_url, headers=headers, params=params)
		response.raise_for_status()

		last_page = None
		link_header = response.headers.get("Link")
		if link_header:
			logger.info(f"Link header found: {link_header}")

			match = re.search(r'<[^>]*page=(\d+)[^>]*>;\s*rel="last"', link_header)
			if match:
				last_page = int(match.group(1))
				logger.info(f"I've found {last_page} pages!")
			else:
				logger.info(
					"No 'last' relation found in Link header. Assuming single page."
				)
				last_page = 1
		else:
			logger.warning("No Link header. Assuming only one page.")
			last_page = 1

		self.wait()
		return last_page

	def basic_extraction(self, endpoint: str, **kwargs):
		logger = logging.getLogger(name=f"{endpoint.upper()}_EXTRACTION")
		headers = {"Authorization": f"Bearer {self.token}"}
		start_page = 1

		params = {"page[number]": start_page, "page[size]": 100}

		if kwargs:
			for key, value in kwargs.items():
				if value is not None:
					params[key] = value

		last_page = self.get_pages(endpoint, params)
		total_pages = last_page

		total_data = []
		request_url = f"{self._base_url}{endpoint}"
		extract_subject = "".join(endpoint.replace("_", " ").title())
		if start_page == total_pages:
			logger.info(f"Extracting {extract_subject} data...")
			response = requests.get(request_url, headers=headers, params=params)
			response.raise_for_status()
			total_data.append(response.json())

		else:
			while params["page[number]"] <= total_pages:
				logger.info(
					f"Extracting data from {extract_subject}, page {params['page[number]']}..."
				)
				response = requests.get(request_url, headers=headers, params=params)
				response.raise_for_status()
				total_data.append(response.json())
				params["page[number]"] += 1
				self.wait()

		logger.info("Returning found data...")

		all_items = []
		for response in total_data:
			all_items.extend(response)

		if len(all_items) == 1:
			return all_items[0]
		else:
			return all_items

	def filtered_extraction(
		self,
		extraction_name: str,
		endpoint: str,
		path_dictionary: dict,
		**kwargs,
	):
		logger = logging.getLogger(f"{extraction_name.upper()}_EXTRACTION")
		headers = {"Authorization": f"Bearer {self.token}"}

		endpoint_format = endpoint.format(**path_dictionary)

		start_page = 1
		params = {"page[number]": start_page, "page[size]": 100}

		if kwargs:
			for key, value in kwargs.items():
				if value is not None:
					params[key] = value

		total_data = []
		last_page = self.get_pages(f"{endpoint_format}", params=params)
		total_pages = last_page

		msg_fmt = "".join(endpoint_format.split("/")[-1].replace("_", " ").title())

		if start_page == total_pages:
			logger.info(
				f"Extracting {msg_fmt} data from {''.join(f'{key}: {value}' for key, value in path_dictionary.items())}..."
			)
			response = requests.get(
				f"{self._base_url}{endpoint_format}", headers=headers, params=params
			)
			response.raise_for_status()
			total_data.append(response.json())

		else:
			while params["page[number]"] <= total_pages:
				logger.info(
					f"Extracting {msg_fmt} data from: {''.join(f'{key}: {value}' for key, value in path_dictionary.items())} page {params['page[number]']}..."
				)
				response = requests.get(
					f"{self._base_url}{endpoint_format}", headers=headers, params=params
				)
				response.raise_for_status()
				total_data.append(response.json())
				params["page[number]"] += 1
				self.wait()

		logger.info("Returning found data...")

		all_items = []
		for response in total_data:
			all_items.extend(response)

		if len(all_items) == 1:
			return all_items[0]
		else:
			return all_items

	@staticmethod
	def set_json(file_name: str, data: str) -> None:
		with open(f"{DATA_DIR}/{file_name}.json", "w", encoding="utf-8") as f:
			json.dump(data, f, ensure_ascii=False, indent=4)

	@staticmethod
	def get_json_data(file_name: str) -> str:
		with open(f"{DATA_DIR}/{file_name}.json", "r") as f:
			json_data = json.load(f)

		return json_data

	@staticmethod
	def wait() -> None:
		"""
		Waits a second.

		Since the API has a wait period, every request we make needs to wait a little. It would get tedious real quick to type "sleep" or "time.sleep(1)"
		"""
		time.sleep(1)
