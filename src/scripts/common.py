from sqlalchemy import create_engine
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import sqlite3

db_path = 'mbdatabase.db'
sql_engine = create_engine(f'sqlite:///{db_path}')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def clean_url(url):
	# Check if the input is a string
	try:
		domain = urlparse(url.strip()).netloc.replace("www.", "").lower()
		if domain and len(domain)>2 and "." in domain:
			return "https://" + domain
	except:
		return None

def store_data_to_rds(dataframe, table_name):
	print(f"Storing data to table {table_name}")
	dataframe.to_sql(table_name, con=sql_engine, index=False, if_exists='replace')