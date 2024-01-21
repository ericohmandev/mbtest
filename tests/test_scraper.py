import pytest, sys
sys.path.append('src/scripts/')
from scrape_eqt_sites_to_rds_tables import *


def test_get_company_id_from_name():
	assert get_company_id_from_name("Some Company (Name)") == "some-company-name"


def test_extract_company_homepage_url_from_eqt_company_site():
	with open("tests/eqt_company_site.txt","r") as file:
		mock_response = file.read()
	soup = BeautifulSoup(mock_response, 'html.parser')
	url = extract_company_homepage_url_from_eqt_company_site(soup)	
	assert url=="https://www.anticimex.com/"

def test_get_people_data_from_eqt_company_site():
	with open("tests/eqt_company_site.txt","r") as file:
		mock_response = file.read()
	soup = BeautifulSoup(mock_response, 'html.parser')
	board_of_directors = get_people_data_from_eqt_company_site(soup, "Board of directors")
	management = get_people_data_from_eqt_company_site(soup, "Management")
	assert board_of_directors == [{'role': 'Chairperson', 'name': 'Jarl Dahlfors'}, {'role': 'Board member', 'name': 'Per Franzén'}, {'role': 'Board member', 'name': 'Carl Johan Renström'}, {'role': 'Board member', 'name': 'Carolina Klint'}, {'role': 'Board member', 'name': 'Dick Seger'}, {'role': 'Board member', 'name': 'Alf Göransson'}, {'role': 'Board member', 'name': 'May Tan'}, {'role': 'Board member', 'name': 'Catherine Halligan'}]
	assert management == [{'role': 'CEO', 'name': 'Staffan Pehrson'}, {'role': 'CFO', 'name': 'Tomas Björksiöö'}, {'role': 'COO', 'name': 'Ebba Bonde'}]