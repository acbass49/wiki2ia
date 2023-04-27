from wiki2ia import get_match
from dotenv import load_dotenv, get_key
import os

#loading environment variables
env_path = os.getcwd() + '/.env'
load_dotenv(dotenv_path = env_path)

citebook_refs = [
    '{{Cite book |url=https://archive.org/details/easterislandisla00dosp |title=Easter Island: Island of Enigmas |last=Dos Passos, John |date=2011 |publisher=Doubleday |isbn=978-0307787057 |oclc=773372948 |access-date=19 March 2019 |archive-url=https://web.archive.org/web/20181209181921/https://archive.org/details/easterislandisla00dosp |archive-date=9 December 2018 |url-status=live }}',
    '{{cite book |author=Churchill, William |year=1912 |title=The Rapanui Speech and the Peopling of Southeast Polynesia |url=https://archive.org/details/easterislandrapa00churrich |url-status=live |archive-url=https://web.archive.org/web/20160404191635/https://archive.org/details/easterislandrapa00churrich |archive-date=4 April 2016}}',
    '{{cite book|last=Barthel |first=Thomas S. |title=The Eighth Land: The Polynesian Settlement of Easter Island |publisher= [[University of Hawaii]] |year=1974 |edition=1978|isbn=0824805534|url=https://archive.org/details/eighthlandpolyne0000bart}}',
    '{{cite book|last1=Fischer|first1=Steven Roger|title=Island at the End of the World|date=2005|publisher=Reaktion Books Ltd.|isbn=978-1861892829|location=London|pages=[https://archive.org/details/islandatendofwor00stev/page/14 14], [https://archive.org/details/islandatendofwor00stev/page/38 38]|author-link=Steven Roger Fischer}}',
    "{{cite book|last1=Salmond|first1=Anne|title=Aphrodite's Island|date=2010|publisher=University of California Press|location=Berkeley|isbn=978-0520261143|page=[https://archive.org/details/aphroditesisland00salm/page/238 238] |url=https://archive.org/details/aphroditesisland00salm|url-access=registration}}",
    '{{cite book |title=The enigmas of Easter Island: Island on the Edge |last1=Flenley |first1=John |last2=Bahn |first2=Paul G. |publisher=Oxford University Press |location=Oxford |year=2003 |pages=156–157 |url=https://archive.org/details/enigmasofeasteri0000flen/page/156/mode/2up |isbn=0192803409}}',
    "{{cite book| last=Englert|first=Sebastian F. |year=1970|title=Island at the Center of the World| url=https://archive.org/details/islandatcenterof00seba| url-access=registration|location=New York|publisher=Charles Scribner's Sons}}"
]

config = {
    's3' :
        {
            'access' : get_key(env_path, "access"),
            'secret' : get_key(env_path, "secret")
        }
}

print(get_match(config=config, cite_string=citebook_refs[2]))
