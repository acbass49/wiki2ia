# Title : Utility Functions
# Author : Alex Bass
# Date : 12 Feb 2023


from internetarchive import get_session
from dotenv import load_dotenv
from os import getcwd, getenv
import json
import re
import pandas as pd
import numpy as np
import logging
from thefuzz import fuzz

#quick utility function
def try_to_pull(json, value):
    try:
        exp = json[value]
        if isinstance(exp, list):
            exp = ','.join(exp)
        return exp
    except KeyError:
        return  None


def get_results(config, cite_book_dict, cap, log):
    '''Output: a dataframe with features to be predicted on
    '''
    assert isinstance(config, dict)
    assert isinstance(cite_book_dict, dict)
    assert isinstance(cap, int)
    
    logging.basicConfig(level=log)
    
    #configuring API connection
    s = get_session(config)

    try:
        title = cite_book_dict['title_wiki'] #grab from wikipedia dict
        title = clean_title(title)
        if title is None or title == "None" or pd.isna(title):
            logging.error("This Wikipedia Reference Has No Title!")
            return None
    except KeyError:
        logging.error("This Wikipedia Reference Has No Title!")
        return None

    search_query = f'collection:internetarchivebooks AND title:{title}'
    response = s.search_items(search_query)
    logging.info(f'There were {response.num_found} results found for this query')
    if isinstance(response.num_found, dict):
        logging.error(f"There is likely a special character in the title that cause the API call to fail: {title}")
        return None
    if response.num_found >= cap:
        logging.warn("The number of API responses exceeded the cap allowed")
        return None
    if response.num_found == 0:
        logging.warn("There were no API responses found for this query")
        return None

    ia_ids = [item['identifier'] for item in response.iter_as_results()]

    for i, ia_id in enumerate(ia_ids):

        #pull relevant metadata
        test_item = s.get_item(ia_id)
        try:
            big_json = test_item.item_metadata['metadata']
        except:
            logging.error(f"There is likely a special character in the title that cause the API call to fail: {title}")
            return None

        ia_link = try_to_pull(big_json, 'identifier-access')

        res_dict = {
            'search_query_ia' : search_query,
            'title_ia' : try_to_pull(big_json, 'title'),
            'author_ia' : try_to_pull(big_json, 'creator'),
            'publisher_ia' : try_to_pull(big_json, 'publisher'),
            'date_ia' :  try_to_pull(big_json, 'date'),
            'year_ia' : try_to_pull(big_json, 'year'),
            'url_ia' : ia_link
        }

        res_dict = {**res_dict, **cite_book_dict}

        tmp = pd.DataFrame(res_dict, index = [0])

        if not 'df' in locals():
            df = tmp
        else:
            df = pd.concat([df, tmp])

    return df


def parse_cite_book(string, keys_to_keep):
    '''
    Input : 
        string : (str) Cite Book string from wikipedia
        keys_to_keep : (list) keys from Cite Book string to keep

    Output : (dict) to be converted into tabular data with relevant information
    '''

    strings = string.split('|')

    #cleaning strings
    strings = strings[1:]
    strings = [re.subn('}','',string)[0] for string in strings]
    strings = [string.rstrip() for string in strings]
    strings = [string.lstrip() for string in strings]

    #creating and filtering dictionary
    strings_dict = dict((re.search(r'(.+)=', string).groups(1)[0], re.search(r'=(.+)', string).groups(1)[0]) for string in strings)

    strings_dict = dict((k, v) for k, v in strings_dict.items() if k in keys_to_keep)

    #renaming keys
    exp = dict((k+'_wiki', v) for k,v in strings_dict.items())

    return(exp)


def pandas_row_to_dict(row_num, data):
    '''
    Input :
        row_num : (int) the row number of pandas df to convert to dict
        data : (pd.DataFrame) the pandas dataframe you want to use

    Output : (dict)
    '''
    results = {}

    for column in data.columns:
        results[column] = data[column].iloc[row_num]

    return results

def clean_title(title):
    if isinstance(title, float):
        return title
    title = title.replace(":", "")
    title = title.replace(",", "")
    title = title.replace(";", "")
    title = title.replace("'", "")
    title = title.replace('"', "")
    title = title.replace('.', "")
    title = title.replace('[', "")
    title = title.replace(']', "")
    title = title.replace('!', "")
    title = title.replace('/', "")
    title = title.replace('\\', "")
    title = title.replace('@', "")
    title = title.replace('*', "")
    title = title.replace('#', "")
    title = title.replace('?', "")
    title = title.replace('%', "")
    title = title.lower()
    title = title.strip()
    return title

def clean_ia_author(author):
    try:
        author.find("(")
    except AttributeError:
        #object is NA
        return author
    if author.find("(") != -1 and author.find(")") != -1:
        author = re.subn(r'[A-Z]\.',"", author)[0]
    author = author.lower()
    author = author.split(',')
    if isinstance(author, list) and len(author) == 1:
        author = author[0]
    elif isinstance(author, list) and len(author) > 1:
        author.reverse()
        author = ' '.join(author)
    author = author.replace(":", "")
    author = author.replace("-", "")
    author = author.replace("[", "")
    author = author.replace("]", "")
    author = author.replace("(", "")
    author = author.replace(")", "")
    author = author.replace("  ", " ")
    author = author.replace("author", "")
    author = author.replace("editor in chief", "")
    author = author.replace("compiler", "")
    author = author.replace("editor", "")
    author = re.subn(r'[0-9]+',"", author)[0]
    author = author.strip()
    if len(list(set(author.split(" ")))) < len(list(author.split(" "))):
        author = list(set(author.split(" ")))
        author = " ".join(author)
        author = author.strip()
    return author

def clean_wiki_publisher(var):
    if isinstance(var, float):
        return var
    try:
        var.find("(")
    except AttributeError:
        #object is NA
        return var
    var = var.replace("[", "")
    var = var.replace("]", "")
    return var

def clean_author_wiki(var):
    if isinstance(var, float):
        return var
    var = var.replace(":", "")
    var = var.replace("-", "")
    var = var.replace("[", "")
    var = var.replace("]", "")
    var = var.replace("(", "")
    var = var.replace(")", "")
    var = var.replace(".", "")
    var = var.lower()
    var = var.strip()
    return var

def get_lev_distance_or_NA(data, columns, partial = False, sort = False):
    assert isinstance(data, pd.DataFrame)
    assert isinstance(columns, list)
    assert len(columns) == 2
    #If partial is True, First column will be fully matched, Second column partially matched
    assert isinstance(columns[0], str)
    assert isinstance(columns[1], str)
    
    out = []
    for i in range(data.shape[0]):
        val1 = data[columns[0]].iloc[i]
        val2 = data[columns[1]].iloc[i]
        if pd.isna(val1) or val1 == "" or pd.isna(val2) or val2 == "":
            out.append(np.nan)
        else:
            if partial and sort:
                out.append(fuzz.partial_token_sort_ratio(val1, val2))
            elif partial:
                out.append(fuzz.partial_ratio(val1, val2))
            elif sort:
                out.append(fuzz.token_sort_ratio(val1, val2))
            else:
                out.append(fuzz.ratio(val1, val2))
    return out

def clean_data(data):
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    
    cols_to_check = ['first_wiki', 'last_wiki', 'first1_wiki', 'last1_wiki', 'first2_wiki', 'last2_wiki']
    tmp_col_list = [x for x in data.columns if x in cols_to_check]
    
    tmp = data[tmp_col_list]

    def quick_combine(row):
        row = row.dropna()
        if len(row) == 0:
            return np.nan
        val = ' '.join(row.astype('str'))
        val = val.strip()
        return val

    data['author_wiki'] = tmp.apply(quick_combine, axis = 1)
    
    data.publisher_wiki = data.publisher_wiki.apply(clean_wiki_publisher)
    data.author_ia = data.author_ia.apply(clean_ia_author)
    data.publisher_ia = data.publisher_ia.apply(clean_wiki_publisher)
    data.author_wiki = data.author_wiki.apply(clean_author_wiki)
    data.title_ia = data.title_ia.apply(clean_title)

    def quick_date_clean(date):
        if isinstance(date, str) and len(date)>4:
            date = date[:4]
            return date
        else:
            return date

    data.date_ia = data.date_ia.apply(quick_date_clean)
    data.drop(columns='year_ia', inplace=True)
    return data

def create_features(data):
    assert isinstance(data, pd.DataFrame)
    assert not data.empty
    
    #lev distance for title
    data['title_match'] = get_lev_distance_or_NA(data, ['title_ia', 'title_wiki'])

    # using partial matching because title_ia is usually more descriptive
    data['title_match_partial'] = get_lev_distance_or_NA(data, ['title_wiki', 'title_ia'], partial = True, sort = True)

    #for author
    data.author_ia = data.author_ia.astype('str')
    data.author_wiki = data.author_wiki.astype('str')

    for var in ['author_ia', 'author_wiki']:
        data[var] = data[var].replace({'nan': np.nan})

    data['author_match'] = get_lev_distance_or_NA(data, ['author_ia', 'author_wiki'])

    data['author_sort'] = get_lev_distance_or_NA(data, ['author_ia', 'author_wiki'], sort = True)

    #for publisher
    data['publisher_match'] = get_lev_distance_or_NA(data, ['publisher_ia', 'publisher_wiki'])

    # using partial matching because publisher_ia is usually more descriptive
    data['publisher_match_partial'] = get_lev_distance_or_NA(data, ['publisher_wiki', 'publisher_ia'], partial = True)

    #year
    def clean(string):
        if pd.isna(string):
            return np.nan
        string = str(string)
        if any(char.isdigit() for char in string) == False:
            return np.nan
        string = re.subn(r'\.[0-9]+',"",string)[0]
        string = re.subn(r'\.',"",string)[0]
        if string:
            try:
                return int(''.join(filter(str.isdigit, string)))
            except:
                print(string)
        else:
            return np.nan

    data['year_wiki'] = data.date_wiki.apply(clean)
    data.date_ia = data.date_ia.apply(clean)

    year_res = []
    for i in range(data.shape[0]):
        val1 = data.date_ia.iloc[i]
        val2 = data.year_wiki.iloc[i]
        if val1 and val2:
            year_res.append(float(val1) == float(val2))
        else:
            year_res.append(np.nan)

    data['year_match'] = year_res

    #year NA
    data['year_NA'] = [np.where(pd.isna(data.year_wiki.iloc[i]) or pd.isna(data.date_ia.iloc[i]), 1, 0) for i in range(data.shape[0])]

    #Author NA
    data['author_NA'] = [np.where(pd.isna(data.author_ia.iloc[i]) or pd.isna(data.author_wiki.iloc[i]), 1, 0) for i in range(data.shape[0])]

    #Publisher NA
    data['publisher_NA'] = [np.where(pd.isna(data.publisher_ia.iloc[i]) or pd.isna(data.publisher_wiki.iloc[i]), 1, 0) for i in range(data.shape[0])]
    
    return data

