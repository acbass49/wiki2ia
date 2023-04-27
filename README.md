# wiki2ia
Capstone Project by Internet Archive: Entity Resolution Algorithm Matching Wikipedia Book Citations to Internet Archive Book API

The purpose of this repo is to improve wikipedia book citation links - giving free access to books cited in Wikipedia with no current link and replacing links that do exist, but are broken. Our model is fully implemented in Python.

example call:
```rb
from wiki2ia import get_match

my_wikipedia_book_citation_string = "{{cite book |author=Churchill, William |year=1912 |title=The Rapanui Speech and the Peopling of Southeast Polynesia |url=https://archive.org/details/easterislandrapa00churrich |url-status=live |archive-url=https://web.archive.org/web/20160404191635/https://archive.org/details/easterislandrapa00churrich |archive-date=4 April 2016}}"

get_match(config=config, cite_string=my_wikipedia_book_citation_string)
```
example response:
```rb
{'match1': {'title_ia': 'the eighth land  the polynesian discovery and settlement of easter island',
  'author_ia': 'thomas s. barthel',
  'publisher_ia': 'Honolulu : University Press of Hawaii',
  'date_ia': 1978,
  'url_ia': 'http://archive.org/details/eighthlandpolyne0000bart',
  'input_citation': '{{cite book|last=Barthel |first=Thomas S. |title=The Eighth Land: The Polynesian Settlement of Easter Island |publisher= [[University of Hawaii]] |year=1974 |edition=1978|isbn=0824805534|url=https://archive.org/details/eighthlandpolyne0000bart}}',
  'match': True}}
```
See vignette.py for a full example call to Internet Archive API to return book matches given a Wikipedia book citation.

Account and configuration instructions for Internet Archive API are found [here](https://archive.org/developers/internetarchive/).
