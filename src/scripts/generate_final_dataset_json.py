from collections import defaultdict
import json
from common import cursor, conn

def create_refined_tables():
	print("Creating refined tables from raw data")
	with open('src/queries/create_dataset.sql', 'r') as file:
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
	data =  extract_sql_to_json_list('src/queries/extract_base_dataset.sql')
	for row in data:
		row["management"] = json.loads(row.get("management","null"))
		row["board_of_directors"] = json.loads(row.get("board_of_directors","null"))
	return data

def extract_funding_data():
	dic = extract_sql_to_json_list('src/queries/extract_funding_data.sql')
	funding_data = defaultdict(list)
	for row in dic:
		temp = dict(row)
		del temp["org_uuid"]
		funding_data[row["org_uuid"]].append(temp)
	return funding_data

def filter_dict(data):
	return {key: value for key, value in data.items() if value is not None}

if __name__ == "__main__":
	create_refined_tables()
	print("Enriching data and saving output")
	base_data = create_base_dictionary()
	funding_data = extract_funding_data()
	for data in base_data:
		data["fundings"] = funding_data.get(data["uuid"])

	result = [filter_dict(data) for data in base_data]
	conn.close()
	with open("result.json", 'w') as json_file:
		json.dump(result, json_file, indent=2,ensure_ascii=False)
	print("Data saved to result.json")