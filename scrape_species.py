'''Scrape species pages'''

import argparse, csv, os, re, time
from datetime import date
import utils.scrape as us
import utils.setup as setup

def get_taxon_page_fields(url:str, output_list:list, base_url:str, run_count:int) -> list:
    '''get fields on a species detail page'''

    if re.match(base_url, url) is not None:
        url = re.sub(base_url, '', url)

    print(f'{run_count} = {base_url}{url}')

    soup = us.get_page_soup(base_url + url)

    page = {
        'order': run_count,
        'url': base_url + url,
        'page_type': 'Species Detail-page',
        'images':None,
        'descrip_text_raw':None,
        'type_descrip':None,
        'type_locality':None,
        'measurements_raw':None,
        'mea_head_body':None,
        'mea_tail':None,
        'mea_weight':None,
        'key_reference': None,
        'taxon': None,
        'author_year': None,
        'common': None,
        'image_credits':None
    }

    # Add match-taxon
    page['taxon'] = us.get_text_from_soup(soup, 'h1')
    page['common'] = us.get_text_from_soup(soup, 'h3')

    p_ids = us.get_html_from_soup(soup, 'p')
    if len(p_ids) > 0:
        for p in p_ids:
            if p.attrs is not None:
                if 'id' in p.attrs:
                    if p['id'] == "zero_margin":
                        page['author_year'] = p.text.strip()


    # Add images
    page_images = us.get_html_from_soup(soup=soup, selector="img")
    page_image_list = []
    if len(page_images) > 0:
        for image in page_images:
            if 'alt' not in image.attrs:
                page_image_list.append(base_url + image['src'])
        if len(page_image_list) > 0:
            page['images'] = ' | '.join(page_image_list).strip()

    # Get Match-page Text:
    page_text_chunks = us.get_html_from_soup(soup=soup, selector="div")
    page_text_list = []
    if len(page_text_chunks) > 0:
        for chunk in page_text_chunks:
            if 'id' in chunk.attrs:
                if chunk['id'] == 'content_main':
                    page_text_list.append(chunk.text)
        if len(page_text_list) > 0:
            page['descrip_text_raw'] = ' | '.join(page_text_list)
            if 'Select species from list' in page['descrip_text_raw']: return

    if page['descrip_text_raw'] is not None:

        # Get Type Descrip
        page['type_descrip'] = re.sub(
            r'(.*\n)*(Type Description\:\n*)(.+)(\nType Locality.*)(\n*.)*', r'\3',
            page['descrip_text_raw']).strip()

        # Get Type Locality
        page['type_locality'] = re.sub(
            r'(.*\n)*(Type Locality\:\n)(.*)(\nMeasurements.*)(\n*.)*', r'\3',
            page['descrip_text_raw']).strip()
        if page['type_locality'] == page['descrip_text_raw']:
            page['type_locality'] = None

        # Get Measurements
        page['measurements_raw'] = re.sub(
            r'(.*\n)*(Measurements\:\n*)(.+)(g[A-Z].+)(\n*.)*', r'\3g',
            page['descrip_text_raw']).strip()
        
        if page['measurements_raw'] is not None:

            # Get Head/Body
            page['mea_head_body'] = re.sub(r'(Head and body\:\s)(.+)(mTail.*)', r'\2m', page['measurements_raw'])

            # Get Tail
            page['mea_tail'] = re.sub(r'(.*Tail length\:\s)(.+)(mWeight.*)', r'\2m', page['measurements_raw'])

            # Get Weight
            page['mea_weight'] = re.sub(r'(.*Weight\:\s)(.+)', r'\2', page['measurements_raw']).strip()

        # Get Key reference
        page['key_reference'] = re.sub(
            r'(.|\n)*(Key Reference\:\n*)(.+)', r'\3',
            page['descrip_text_raw']).strip()

        # get image credit
        # <p id="credit">

        # 

    # Get list of Match-page image-URLs
    page_images = us.get_html_from_soup(soup=soup, selector="img")
    page_image_list = []
    if len(page_images) > 0:
        for image in page_images:
            if 'alt' not in image.attrs:
                page_image_list.append(base_url + image['src'])
        if len(page_image_list) > 0:
            page['images'] = ' | '.join(page_image_list)


    # Get Image credits
    page_image_credits = us.get_html_from_soup(soup=soup, selector="font")

    page_credit_list = []

    for credit in page_image_credits:
        if 'size' in credit.attrs:
            if credit['size'] == '2':
                page_credit_list.append(credit.text)

    if len(page_credit_list) > 0:
        page['image_credits'] = ' | '.join(page_credit_list)

    if page not in output_list:
        output_list.append(page)
    
    time.sleep(0.5)

    return


def main():
    '''main function'''

    config = setup.get_config()
    base_url = config['BASE_URL']

    # Set up command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("start_url", help="top level URL to use as starting point")
    parser.add_argument("output_path", help="Output path (with trailing '/')")
    args = parser.parse_args()

    run_count = 0

    # First, we need to get all of the URLs we need to scrape
    start_url = args.start_url

    soup = us.get_page_soup(start_url)

    soup_links = us.get_html_from_soup(soup=soup, selector="a") 

    soup_species_list = []

    # Get Taxon URLs
    if soup_links is not None and len(soup_links) > 0:

        for species_link in soup_links:

            if "species" in species_link['href']:

                species_link_url = species_link['href']
                if re.match(base_url, species_link_url) is not None:
                    species_link_url = re.sub(base_url, '', species_link_url)
                
                species_url = {'url':base_url + species_link_url}

                if species_url not in soup_species_list:
                    soup_species_list.append(species_url)


    output_list = []

    # Test small batch
    soup_species_list = soup_species_list[0:5]

    if len(soup_species_list) > 0:

        for species in soup_species_list:

            run_count += 1

            get_taxon_page_fields(species['url'], output_list, base_url, run_count)
    
    # Check if dir exists, and if not, make it
    output_path = args.output_path

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    date_suffix = re.sub(r'\-|\s*|\:|\..*', '', str(date.today()))

    with open(f"{output_path}scraped_taxon_{date_suffix}.csv", encoding='utf-8', mode='w') as scraped_urls:
        col_names = list(output_list[0].keys())
        print(col_names)
        write = csv.DictWriter(f=scraped_urls, fieldnames=col_names)
        write.writeheader()
        write.writerows(output_list)


if __name__ == '__main__':
    main()