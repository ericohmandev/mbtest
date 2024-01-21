import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from common import clean_url, store_data_to_rds
import json
from unidecode import unidecode


EQT_DIVESTMENTS_URL = 'https://eqtgroup.com/current-portfolio/divestments'
EQT_PORTFOLIO_URL = "https://eqtgroup.com/current-portfolio"


def get_company_id_from_name(company_name):
	cleaned_string = company_name.lower()
	cleaned_string = cleaned_string.replace("ö","oe")
	cleaned_string = cleaned_string.replace("ä","ae")
	cleaned_string = unidecode(cleaned_string)
	cleaned_string = re.sub(r'[^a-zA-Z0-9]+', '-', cleaned_string)
	cleaned_string = cleaned_string.strip('-')
	return cleaned_string

def get_eqt_company_url_from_company_name(company_name):
	return f'{EQT_PORTFOLIO_URL}/{get_company_id_from_name(company_name)}'

def get_people_data_from_eqt_company_site(soup, section_name):
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

def extract_company_homepage_url_from_eqt_company_site(soup):
	web_elements = soup.find_all('li', class_='flex border-b border-neutral-lighter py-7')
	for web_element in web_elements:
		if web_element.find('span', text='Web') and web_element.find('a', class_='transition-hover hover:opacity-hover focus:opacity-hover focus:outline-none text-primary'):
			href_value = web_element.find('a')['href']
			if href_value:
				return href_value
	return None

def scrape_eqt_company_site_for_data(company_name):
	url = get_eqt_company_url_from_company_name(company_name)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	url = extract_company_homepage_url_from_eqt_company_site(soup)
	board_of_directors = get_people_data_from_eqt_company_site(soup, "Board of directors")
	management = get_people_data_from_eqt_company_site(soup, "Management")
	cleaned_url = clean_url(url)
	return {"url":url, "cleaned_url":cleaned_url,"board_of_directors":json.dumps(board_of_directors,ensure_ascii=False),"management":json.dumps(management,ensure_ascii=False)}

def scrape_all_companies_on_portfolio_site(url,is_divestment):
	print(f"Scraping data from {url}")
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	repeating_elements = soup.find_all('span', class_='inline-block')
	result = []
	for element in repeating_elements:
		data=parse_company_data_from_html_element(element)
		if data:
			data["is_divestment"]=is_divestment
			eqt_company_site_data = scrape_eqt_company_site_for_data(data.get("company"))
			data = {**data, **eqt_company_site_data}
			result.append(data)
	print(f"Scraping done, data for {str(len(result))} companies extracted")
	return result

def parse_company_data_from_html_element(element):
	company_name = element.text.strip()
	parent_container = element.find_parent('li', class_='flex flex-col border-t border-neutral-light cursor-pointer sm:cursor-default')
	if parent_container:
		company_name = parent_container.find('span', class_='inline-block').text.strip()
		sector = parent_container.find('span', class_='font-medium', text='Sector').find_next('span').text.strip()
		country = parent_container.find('span', class_='font-medium', text='Country').find_next('span').text.strip()
		fund = parent_container.find('span', class_='font-medium', text='Fund').find_next('a', class_='text-primary font-medium').text.strip()
		entry_year = parent_container.find('span', class_='font-medium', text='Entry').find_next('span').text.strip()
		exit_year = parent_container.find('span', class_='font-medium', text='Exit').find_next('span').text.strip() if parent_container.find('span', class_='font-medium', text='Exit') else None
		company_id = get_company_id_from_name(company_name)
		return {"eqt_company_id":company_id,"company":company_name,"sector":sector,"country":country,"fund":fund,"entry_year":entry_year,"exit_year":exit_year}


def scrape_eqt_websites_to_dataframe():
	cleaned_data = scrape_all_companies_on_portfolio_site(EQT_PORTFOLIO_URL,is_divestment=False)
	cleaned_data += scrape_all_companies_on_portfolio_site(EQT_DIVESTMENTS_URL,is_divestment=True)
	return pd.DataFrame(cleaned_data)


if __name__ == "__main__":
	scraped_data_df = scrape_eqt_websites_to_dataframe()
	store_data_to_rds(scraped_data_df, "portfolio")
