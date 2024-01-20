from collections import defaultdict
import json
from common import cursor



def create_tables():
	with open('queries/create_dataset.sql', 'r') as file:
	    sql_queries = file.read()
	queries = sql_queries.split(';')
	for query in queries:
		cursor.execute(query)
	conn.commit()


def extract_sql_to_json_list(file_name):
	with open(file_name, 'r') as file:
	    query = file.read()

	cursor.execute(query)
	rows = cursor.fetchall()

	columns = [column[0] for column in cursor.description]
	base_dataset = [dict(zip(columns, row)) for row in rows]
	return base_dataset


def create_base_dictionary():
	return extract_sql_to_json_list('queries/extract_base_dataset.sql')

def extract_funding_data():
	dic = extract_sql_to_json_list('queries/extract_funding_data.sql')
	funding_data = defaultdict(list)
	for row in dic:
		temp = dict(row)
		del temp["org_uuid"]
		funding_data[row["org_uuid"]].append(temp)
	return funding_data

if __name__ == "__main__":
	create_tables()
	base_data = create_base_dictionary()
	funding_data = extract_funding_data()
	for data in base_data:
		data["fundings"] = funding_data.get(data["uuid"],[])
	conn.close()
	with open("result.json", 'w') as json_file:
		json.dump(base_data, json_file, indent=2)
