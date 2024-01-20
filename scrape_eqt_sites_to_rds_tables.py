import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from common import clean_url, store_data_to_rds


'''
This scraping script goes into the EQT portfolio sites, and for each company stores information.
In order to get the url of the website, which is stored within a specific url for the company at EQT,
the script also scrapes that specific site and saves the url. 

The data points saved for each company:
company - the name of the company
sector - The sector, i.e. Technology etc
country - Full country name, such as Sweden, Norway
fund - Which fund the investment came from
entry_year - What year did EQT invest in the company
exit_year - What year did EQQT exit their investment
url - The raw url for the company listed on EQTs site
cleaned_url - The cleaned url, used mainly for joining
'''

def transform_company_name_to_eqt_url(company_name):
	company_name = company_name.lower()
	company_name = company_name.replace("ö","oe")
	company_name = company_name.replace("å","a")
	company_name = company_name.replace("ä","ae")
	# Replace everything that is not a letter or number with a dash
	cleaned_string = re.sub(r'[^a-zA-Z0-9]+', '-', company_name)

	# Remove leading and trailing dashes
	cleaned_string = cleaned_string.strip('-')

	# Lowercase the string
	cleaned_string = cleaned_string.lower()

	return f'https://eqtgroup.com/current-portfolio/{cleaned_string}'

def scrape_eqt_url_for_company_homepage_url(company_name):
	url = transform_company_name_to_eqt_url(company_name)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	web_elements = soup.find_all('li', class_='flex border-b border-neutral-lighter py-7')
	for web_element in web_elements:
		# Check if the structure matches the desired one
		if web_element.find('span', text='Web') and web_element.find('a', class_='transition-hover hover:opacity-hover focus:opacity-hover focus:outline-none text-primary'):
			# Extract the href attribute
			href_value = web_element.find('a')['href']
			if href_value:
				return href_value
	return None


def scrape_portfolio_website(url,is_divestment):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	repeating_elements = soup.find_all('span', class_='inline-block')
	result = []
	for element in repeating_elements:
		data = parse_json_from_container(element)
		print(data)
		if data:
			data["is_divestment"]=is_divestment
			result.append(data)
	return result


def parse_json_from_container(element):
	company_name = element.text.strip()
	parent_container = element.find_parent('li', class_='flex flex-col border-t border-neutral-light cursor-pointer sm:cursor-default')
	if parent_container:
		string = parent_container.text
		# Pattern for company name
		company_pattern = re.compile(r'(.*?)Sector')
		company_match = company_pattern.search(string)
		company_name = company_match.group(1).strip() if company_match else None

		# Pattern for sector
		sector_pattern = re.compile(r'Sector(.*?)Country')
		sector_match = sector_pattern.search(string)
		sector = sector_match.group(1).strip() if sector_match else None

		# Pattern for country
		country_pattern = re.compile(r'Country(.*?)Fund')
		country_match = country_pattern.search(string)
		country = country_match.group(1).strip() if country_match else None

		# Pattern for fund
		fund_pattern = re.compile(r'Fund(.*?)Entry')
		fund_match = fund_pattern.search(string)
		fund = fund_match.group(1).strip() if fund_match else None

		# Pattern for entry year
		entry_year_pattern = re.compile(r'Entry(\d{4})(?:Exit|$)')
		entry_year_match = entry_year_pattern.search(string)
		entry_year = entry_year_match.group(1).strip() if entry_year_match else None

		# Pattern for exit year (always after entry)
		exit_year_pattern = re.compile(r'Exit(\d{4})')
		exit_year_match = exit_year_pattern.search(string)
		exit_year = exit_year_match.group(1).strip() if exit_year_match else None

		url = scrape_eqt_url_for_company_homepage_url(company_name)
		cleaned_url = clean_url(url)

		return {"company":company_name,"sector":sector,"country":country,"fund":fund,"entry_year":entry_year,"exit_year":exit_year, "url":url, "cleaned_url":cleaned_url}


def scrape_eqt_websites_to_dataframe():
	portfolio_url = 'https://eqtgroup.com/current-portfolio/'
	divestments_url = 'https://eqtgroup.com/current-portfolio/divestments'
	cleaned_data = scrape_portfolio_website(portfolio_url,is_divestment=False) + scrape_portfolio_website(divestments_url,is_divestment=True)
	return pd.DataFrame(cleaned_data)


if __name__ == "__main__":
	scraped_data_df = scrape_eqt_websites_to_dataframe()
	store_data_to_rds(scraped_data_df, "portfolio")




