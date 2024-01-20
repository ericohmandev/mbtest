# Makefile for creating a virtual environment, installing dependencies, and running Python scripts

.PHONY: all clean

all: venv install run_all

venv:
	python3 -m venv venv

install: venv
	venv/bin/pip install -r requirements.txt

run_all: install
	venv/bin/python3 transform_json_data_to_rds_tables.py
	venv/bin/python3 scrape_eqt_sites_to_rds_tables.py
	venv/bin/python3 generate_final_dataset_json.py