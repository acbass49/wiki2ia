# Title : Rivanna Script to Run on 5 different servers
# Author : Alex Bass
# Date : 15 March 2023

#Imported `Test_Set_v5`, utils.py, .env, and this script to run on 5 partitions in cloud

#set partition number 1-5
partition = 1
print(f"called {partition}")

import pandas as pd
import os

os.chdir('/Users/alex/Library/CloudStorage/OneDrive-Personal/DSCapstone')
data = pd.read_csv("Test_Set_v5.csv")

data = data.iloc[100:,] #removing first 100 to put in golden set

fifths = round(data.shape[0]/5)

instructions = {
    1 : [0, fifths],
    2 : [fifths, fifths*2],
    3 : [fifths*2, fifths*3],
    4 : [fifths*3, fifths*4],
    5 : [fifths*4, data.shape[0]]
}

# Begin Main Script

from utils import get_results, pandas_row_to_dict, clean_wiki_publisher, clean_ia_author, clean_author_wiki, clean_title
from dotenv import load_dotenv, get_key
import time

#timing script
start_time = time.time()

#loading environment variables
env_path = os.getcwd() + '/.env'

load_dotenv(dotenv_path = env_path)

config = {
    's3' :
        {
            'access' : get_key(env_path, "access"),
            'secret' : get_key(env_path, "secret")
        }
}

#results skipped because of cap
log = []

#grabbing ranges for loops from instructions
start = instructions[partition][0]
end = instructions[partition][1]

for i in range(start,end):
    
    try:
        if (i)%500==0:
            print(f'{i-start} out of {end-start}')

        cite_book_dict = {}

        cite_book_dict = pandas_row_to_dict(i, data)

        tmp = get_results(config, cite_book_dict, cap = 150)
        try:
            tmp['query_count'] = i+1
        except:
            pass
        if tmp is None:
            pass
        elif isinstance(tmp, int):
            log.append(tmp)
        elif not 'exp_data' in locals():
            exp_data = tmp
            log.append(3)
        else:
            exp_data = pd.concat([exp_data, tmp])
            log.append(3)
    except:
        pass

# 0 Title or URL are NA; 1 number of responses greater than cap; 2 No results found in API; 3 success
def quick_summary(results, num, name):
    num_true = sum([x == num for x in results])
    total_num = len(results)
    p_true = str(round((num_true/total_num)*100))
    print(f'for {name}...')
    print(f'occured: {str(num_true)}')
    print(f'percent: {p_true}%')
    return None

quick_summary(log, 0, 'Title or URL are NA')
quick_summary(log, 1, 'Number of responses greater than cap')
quick_summary(log, 2, 'No Results Found in API')
quick_summary(log, 3, 'Success')


try:
    exp_data.publisher_wiki = exp_data.publisher_wiki.apply(clean_wiki_publisher)
    exp_data.author_ia = exp_data.author_ia.apply(clean_ia_author)
    exp_data.publisher_ia = exp_data.publisher_ia.apply(clean_wiki_publisher)
    exp_data.author_wiki = exp_data.author_wiki.apply(clean_author_wiki)
    exp_data.title_ia = exp_data.title_ia.apply(clean_title)

    def quick_date_clean(date):
        if isinstance(date, str) and len(date)>4:
            date = date[:4]
            return date
        else:
            return date

    exp_data.date_ia = exp_data.date_ia.apply(quick_date_clean)
    exp_data.drop(columns='year_ia', inplace=True)
except:
    print("data cleaning step errored out")

exp_data.to_csv(f"training_set_{partition}.csv",index=False)

print(f'This script took {round((((time.time() - start_time)/60)/60)/24, 2)} days')


#extra part to execute later
os.chdir('/Users/alex/Library/CloudStorage/OneDrive-Personal/DSCapstone')

data_dirs = [x for x in os.listdir() if "training" in x][1:]

for data in data_dirs:
    if 'out' not in locals():
        out = pd.read_csv(data)
    else:
        out = pd.concat([out, pd.read_csv(data)], ignore_index=True)

out.to_csv("training_set_final.csv")
