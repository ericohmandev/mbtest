# Makefile for creating a virtual environment, installing dependencies, and running Python scripts

.PHONY: all clean

venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip

install: venv
	venv/bin/pip install -r requirements.txt

run_pipeline: install
	venv/bin/python3 transform_json_data_to_rds_tables.py
	venv/bin/python3 scrape_eqt_sites_to_rds_tables.py
	venv/bin/python3 generate_final_dataset_json.py