from utils import get_results, parse_cite_book, clean_data, create_features, pandas_row_to_dict
import time
import logging
import pickle
import numpy as np

def get_match(config, cite_string, cap = 500, log_level = "info", return_dataframe = False, all_results = False):
    
    start = time.time()
    
    if log_level == "error":
        logging.basicConfig(level=logging.ERROR)
        log = logging.ERROR
    elif log_level == "info":
        logging.basicConfig(level=logging.INFO)
        log = logging.INFO
    elif log_level == "debug":
        logging.basicConfig(level=logging.DEBUG)
        log = logging.DEBUG
    elif log_level == "warning":
        logging.basicConfig(level=logging.WARNING)
        log = logging.WARNING
    elif log_level == "critical":
        logging.basicConfig(level=logging.CRITICAL)
        log = logging.CRITICAL
    else:
        raise Exception("Please set the log level to an accepted value: [error, info, debug, warning, critical]")
    
    keys_to_keep = [
        'title',
        'last',
        'first',
        'first1',
        'last1',
        'first2',
        'last2',
        'date',
        'publisher',
        'url'
    ]
    cite_book_dict = parse_cite_book(cite_string, keys_to_keep)
    
    if 'date_wiki' not in cite_book_dict.keys():
        cite_book_dict['date_wiki'] = np.nan
    
    if 'publisher_wiki' not in cite_book_dict.keys():
        cite_book_dict['publisher_wiki'] = np.nan
    
    data = get_results(config, cite_book_dict, cap, log)
    if data.empty:
        logging.warn("No results. Returning None Object.")
        return None
    
    data = clean_data(data)
    
    data.reset_index(inplace=True, drop=True)
    ia_links = data['url_ia']
    
    data = create_features(data)
    
    #filter columns to those that were originally fit
    to_predict = data[['title_match','author_match', 'publisher_match', 'year_match', 'year_NA', 'author_NA', 'publisher_NA', 'title_match_partial', 'publisher_match_partial', 'author_sort']].copy()
    
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    data['match'] = loaded_model.predict(to_predict)
    data['match'] = data['match'].astype('bool')
    data['url_ia'] = ia_links
    
    results = data
    results['input_citation'] = cite_string
    if not all_results:
        results = results.query('match == True')
    
    results = results[['title_ia', 'author_ia', 'publisher_ia', 'date_ia', 'url_ia', 'input_citation', 'match']]
    
    there_are_matches = results.query('match == True').empty
    num_matches = results.query('match == True').shape[0]
    
    if there_are_matches:
        logging.info("There were no matches present.")
        if not all_results:
            return None
    
    exp = {}
    for i in range(results.shape[0]):
        exp[f'match{i+1}'] = pandas_row_to_dict(i, results)
    
    logging.info(f"Success. {num_matches} total matches. Returning results.")
    end = time.time()
    logging.info(f"Process took {round((end - start)/60, 2)} minutes total.")
    
    if return_dataframe:
        return results
    return exp
