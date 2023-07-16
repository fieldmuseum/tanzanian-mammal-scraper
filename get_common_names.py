'''Scrape species pages'''

import argparse, csv, json, os, re, requests, time
from datetime import date
import wikipediaapi as wiki
import utils.setup as setup
import utils.csv as utils_csv


def get_iucn_common_name(taxon, iucn_url) -> list:
    '''get a list of dicts '''

    common_names_result = None

    # print(iucn_url)

    iucn_response = requests.get(iucn_url)

    # print(iucn_response.status_code)

    if iucn_response.status_code < 300:
        # is not None and 'result' in iucn_response:
        if iucn_response.text is not None:
            common_names_raw = iucn_response.text
            print(common_names_raw)
            common_names = json.loads(common_names_raw)
            if 'result' in common_names:
                common_names_result = common_names['result']
    
    taxon_common_names = {'taxon':taxon, 'common_names': common_names_result}

    # print(common_names)

    time.sleep(3)

    return taxon_common_names

# def get_wikipedia_common_names(taxon, wiki_user_agent) -> list:
#     '''
#     Get a list of dicts {'common':<retrieved_name>} from the Wikipedia API
#     For different languages, may be able to point o en/es/fr/etc urls
#     '''

#     if taxon is None:
#         taxon = 'Myotis morrisi'

#     wiki_api_url_en = 'http://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles='
#     wiki_api_suffix = '&explaintext=1&exsectionformat=wiki'

#     wiki_api_url = wiki_api_url_en + taxon + wiki_api_suffix
    
#     # wiki_html = wiki.Wikipedia(wiki_user_agent, 
#     #                                    'en', 
#     #                                    extract_format=wiki.ExtractFormat.HTML)
    
#     r = requests.get(url=wiki_api_url, headers={'User-Agen':wiki_user_agent})

#     # css_select = '.infobox > tbody:nth-child(1) > tr:nth-child(1) > th:nth-child(1)'


def main():
    '''main function'''

    config = setup.get_config()

    # Set up command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="input CSV that includes a 'taxon' column that contains scientific names")
    parser.add_argument("output_path", help="Output path (with trailing '/')")
    args = parser.parse_args()
    
    # setup IUCN API call for common names
    iucn_base_url = config['IUCN_BASE_URL']
    iucn_token = config['IUCN_TOKEN']

    # # setup Wikipedia API call
    # wiki_user_agent = config['WIKI_USER_AGENT']

    taxon_list = utils_csv.rows(args.input_csv)

    # # Test small batch
    # taxon_list = taxon_list[0:2]

    common_name_list = []

    # Get Common Names
    for row in taxon_list:

        taxon = row['taxon']

        if taxon is not None and len(taxon) > 0:

            species_url = f"{iucn_base_url}/api/v3/species/common_names/{taxon}?token={iucn_token}"
            taxon_common_name = get_iucn_common_name(taxon, species_url)

            time.sleep(0.5)

            common_name_list.append(taxon_common_name)
 
    # Check if dir exists, and if not, make it
    output_path = args.output_path

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    date_suffix = re.sub(r'\-|\s*|\:|\..*', '', str(date.today()))

    with open(f"{output_path}taxon_common_names_{date_suffix}.csv", encoding='utf-8', mode='w') as all_names:
        col_names = list(common_name_list[0].keys())
        print(col_names)
        write = csv.DictWriter(f=all_names, fieldnames=col_names)
        write.writeheader()
        write.writerows(common_name_list)
    
    f = open(f"{output_path}taxon_common_names_{date_suffix}.json", 'w', encoding='utf-8')
    f.write(json.dumps(common_name_list, indent=True, ensure_ascii=False))
    f.close()


if __name__ == '__main__':
    main()