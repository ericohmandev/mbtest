import pandas as pd
from common import clean_url, store_data_to_rds


#Load the files into pandas format
funding_df = pd.read_json('data/interview-test-funding.json.gz', lines=True)
organisation_df = pd.read_json('data/interview-test-org.json.gz', lines=True)
store_data_to_rds(funding_df,"funding")


'''
Since the homepage_url took on all sorts of formats, and it seemed to be the best
key to join data with the portfolio companies, this needed to be cleaned before
inserting into rds.
'''
organisation_df['cleaned_url'] = organisation_df['homepage_url'].apply(clean_url)
store_data_to_rds(organisation_df, "organisation")