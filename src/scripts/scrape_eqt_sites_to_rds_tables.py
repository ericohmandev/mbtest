import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from common import clean_url, store_data_to_rds
import json


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

def get_company_id(company_name):
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
	return cleaned_string	


def transform_company_name_to_eqt_url(company_name):
	return f'https://eqtgroup.com/current-portfolio/{get_company_id(company_name)}'

def get_section_from_company_site(soup, section_name):
	result = []
	section = soup.find('h3', text=section_name)
	if section:
		section = section.find_next("ul")
		for li in section.find_all("li"):
			role = li.find('div', class_='flex-1 font-light')
			name = li.find('div', class_='flex-1 font-medium')
			if role and name:
				result.append({'role': role.text.strip(), 'name': name.text.strip()})
	return result if result else None


def extract_company_homepage_url(soup):
	web_elements = soup.find_all('li', class_='flex border-b border-neutral-lighter py-7')
	for web_element in web_elements:
		# Check if the structure matches the desired one
		if web_element.find('span', text='Web') and web_element.find('a', class_='transition-hover hover:opacity-hover focus:opacity-hover focus:outline-none text-primary'):
			# Extract the href attribute
			href_value = web_element.find('a')['href']
			if href_value:
				return href_value
	return None


def scrape_eqt_company_for_data(company_name):
	url = transform_company_name_to_eqt_url(company_name)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	url = extract_company_homepage_url(soup)
	board_of_directors = get_section_from_company_site(soup, "Board of directors")
	management = get_section_from_company_site(soup, "Management")
	return {"url" : url, "board_of_directors": board_of_directors,"management":management}




def scrape_portfolio_website(url,is_divestment):
	print(f"Scraping data from {url}")
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	repeating_elements = soup.find_all('span', class_='inline-block')
	result = []
	for element in repeating_elements:
		data = parse_json_from_container(element)
		if data:
			data["is_divestment"]=is_divestment
			result.append(data)
	print(f"Scraping done, data for {str(len(result))} companies extracted")
	return result



def parse_json_from_container(element):
	company_name = element.text.strip()
	parent_container = element.find_parent('li', class_='flex flex-col border-t border-neutral-light cursor-pointer sm:cursor-default')
	if parent_container:
		company_name = parent_container.find('span', class_='inline-block').text.strip()
		sector = parent_container.find('span', class_='font-medium', text='Sector').find_next('span').text.strip()
		country = parent_container.find('span', class_='font-medium', text='Country').find_next('span').text.strip()
		fund = parent_container.find('span', class_='font-medium', text='Fund').find_next('a', class_='text-primary font-medium').text.strip()
		entry_year = parent_container.find('span', class_='font-medium', text='Entry').find_next('span').text.strip()
		exit_year = parent_container.find('span', class_='font-medium', text='Exit').find_next('span').text.strip() if parent_container.find('span', class_='font-medium', text='Exit') else None

		eqt_company_website_data = scrape_eqt_company_for_data(company_name)
		url = eqt_company_website_data.get("url")
		cleaned_url = clean_url(url)
		company_id = get_company_id(company_name)
		return {"eqt_company_id":company_id,"company":company_name,"sector":sector,"country":country,"fund":fund,"entry_year":entry_year,"exit_year":exit_year, "url":url, "cleaned_url":cleaned_url,"board_of_directors":json.dumps(eqt_company_website_data.get("board_of_directors"),ensure_ascii=False),"management":json.dumps(eqt_company_website_data.get("management"),ensure_ascii=False)}


def scrape_eqt_websites_to_dataframe():
	portfolio_url = 'https://eqtgroup.com/current-portfolio/'
	divestments_url = 'https://eqtgroup.com/current-portfolio/divestments'
	cleaned_data = scrape_portfolio_website(portfolio_url,is_divestment=False) + scrape_portfolio_website(divestments_url,is_divestment=True)
	return pd.DataFrame(cleaned_data)


if __name__ == "__main__":
	scraped_data_df = scrape_eqt_websites_to_dataframe()
	store_data_to_rds(scraped_data_df, "portfolio")
