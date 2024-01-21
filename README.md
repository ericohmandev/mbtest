# EQT Pipeline assignment
This readme is a notebook on how the solution was done, not a common readme. To run the pipeline, all you need to do is read the "Run the solution" part below, the rest of the readme is around the process.

## Run the solution
```sh
make run_pipeline
```

Running this will download all files, scrape the sites, transform and join the data into the resulting file:
```sh
result.json
```
Which is stored in this repo.

## Run tests
```sh
make run_tests
```


## Background
The goal of the assignment is to create a dataset of the companies that are relevant to EQT. 
The base dataset is given by scraping the companies at EQTs website
- [EQT Current Portfolio](https://eqtgroup.com/current-portfolio/)
- [EQT Divestments](https://eqtgroup.com/current-portfolio/)

This is around 400 companies. 

The data we have to enrich these 400 companies are given from the datasets in gcs
- interview-test-funding.json.gz
- interview-test-org.json.gz

## Scraping the data
The scraping script goes into the EQT portfolio sites, and for each company stores information.
In order to get the url of the website, which is stored within a specific url for the company at EQT,
the script also scrapes that specific site and saves the url. 

The data points saved for each company:
- **company** - the name of the company
- **sector** - The sector, i.e. Technology etc
- **country** - Full country name, such as Sweden, Norway
- **fund** - Which fund the investment came from
- **entry_year** - What year did EQT invest in the company
- **exit_year** - What year did EQQT exit their investment
- **url** - The raw url for the company listed on EQTs site
- **cleaned_url** - The cleaned url, used mainly for joining
- **is_divestment** - Has EQT divested from the company or not
- **management** - Persons listed as management and what role they have
- **board_of_directors** - Persons listed as board of directors and what role they have

## Exploring and enriching the data
At first glance, it seemed simple to enrich the base data with the gcs data, but the biggest issue here seemed to be that there was no obvious way of joining the data with base data. Some examples:
- Names are not unique in gcs data, and they are not even unique on a country level. So joining on this would not give any guarantee that the data is enriched with the correct data.
- The only key that seemed reasonable was the url of the company, this also had some issues which could somewhat be resolved by cleaning, but almost half of the companies does not have an url listed on the EQT website. Although, the majority of the current holdings (not divested) do have an URL, so perhaps that is more important.
- Some companies appeared twice at EQT, just a duplicate
    - Broadnet 
    - SSP
- These companies appeared once in portfolio, and once in divested. How should this be interpreted?
    - Anticimex
    - DELTA Fiber
    - WS Audiology
- Multiple companies with the same url in the organisation dataset (from gcs) 
    - Examples, the homepage url https://www.iver.com/ maps to both Iver and Iver Sverige

The strategy to solve for all of this was to:
- From the EQT websites, deduplicate companies and if a company is in both divested and in portfolio, it will be seen as not divested.
- The only key that will be used to join the datasets, will be the cleaned url. If there are multiple hits on that join, it will only take one row and the prioritoization will be the row with the company name being equal.

In general, there seems to be no way to really guarantee the correctness when joining these datasets, so it really depends on what the end goal here is. If it should be 100% correct, then this could probably not be done in an automatic pipeline with these datasets. Instead there would need to be some manual work and go through the companies one by one to get the corresponding uuid if it exists for the company. There are a bunch of different strategies with edge cases one could employ that could explore with more time.

## Final output
Final output is the result.json file, the instructions said to store it in json / avro in any data storage, but for sake of simplicity this will just be a file here. If it were to be in a nosql database, like dynamodb, each element in this list could be stored there, and the suggested key could be the a cleaned version of the company name or some other generated company_id.