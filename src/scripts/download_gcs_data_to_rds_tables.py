import pandas as pd
from common import clean_url, store_data_to_rds
import io, requests, gzip

FUNDING_DATA_URL = "https://storage.googleapis.com/motherbrain-external-test/interview-test-funding.json.gz"
ORGANISATION_DATA_URL = "https://storage.googleapis.com/motherbrain-external-test/interview-test-org.json.gz"

def download_data_from_url_to_df(url):
	print(f"Downloading data from {url} into dataframe")
	response = requests.get(url)
	with gzip.GzipFile(fileobj=io.BytesIO(response.content), mode='rb') as decompressed_file:
		df = pd.read_json(decompressed_file, lines=True)
	return df


if __name__ == "__main__":
	funding_df = download_data_from_url_to_df(FUNDING_DATA_URL)
	store_data_to_rds(funding_df,"funding")

	organisation_df = download_data_from_url_to_df(ORGANISATION_DATA_URL)
	organisation_df['cleaned_url'] = organisation_df['homepage_url'].apply(clean_url)
	store_data_to_rds(organisation_df, "organisation")