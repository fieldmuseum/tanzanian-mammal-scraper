'''Scraper for Tanzanian Mammals ID Key Site'''

import argparse, csv, os, re, time
from datetime import datetime, date
import utils.scrape as us
import utils.setup as setup

def get_child_urls(url:str, output_list:list, base_url:str, run_count:int) -> list:
    '''get a list of each child URL and its own child-option-URLs'''

    time.sleep(4)

    if run_count == "stop": return
    run_count += 1

    if re.match(base_url, url) is not None:
        url = re.sub(base_url, '', url)

    print(f'{run_count} = {base_url}{url}')

    soup = us.get_page_soup(base_url + url)

    page = {
        'order': run_count,
        'url': base_url + url,
        'page_type': 'Option-page',
        'section': None,
        'opt_a_link': None,
        'opt_a_text': None,
        'opt_a_img': None,
        'opt_b_link': None,
        'opt_b_text': None,
        'opt_b_img': None,
        'other_images':None,
        'other_text':None,
        'match_taxon': None,
        'match_common': None,
        'image_credits':None
    }
    
    # - For Current child pages [if any] - 'Select' link

    # Get list of all URLs on the current key-page
    soup_links = us.get_html_from_soup(soup=soup, selector="a")

    soup_child_list = []

    # Get Option-page Child URLs
    if soup_links is not None and len(soup_links) > 0:

        for child_link in soup_links:

            if re.match(r'Chagua', child_link.get_text()) is not None:
            # if "Select" in child_link.get_text():

                child_link_url = child_link['href']
                if re.match(base_url, child_link_url) is not None:
                    child_link_url = re.sub(base_url, '', child_link_url)

                soup_child_list.append({'url':base_url + child_link_url})

                time.sleep(2.5)

                run_count = get_child_urls(base_url + child_link_url, output_list, base_url, run_count)
    
    if len(soup_child_list) > 0:
        # Get Option-page specific fields

        page['opt_a_link'] = soup_child_list[0]['url']
        page['opt_b_link'] = soup_child_list[1]['url']

        # Get Option-page Text:
        page_text_chunks = us.get_html_from_soup(soup=soup, selector="td")

        page_text_list = []
        
        if len(page_text_chunks) > 0:
            for chunk in page_text_chunks:
                if 'colspan' in chunk.attrs:
                    if chunk['colspan'] == '2':
                        if re.match(r'Sehemu\:\s*', chunk.text) is not None:
                            # print(chunk.text)
                            page['section'] = chunk.text.strip()
                if 'width' in chunk.attrs:
                    if chunk['width'] == '300':
                        if re.match(r'Chaguo (A|B)', chunk.text) is None:
                            page_text_list.append(chunk.text)
            if len(page_text_list) > 0:
                page['opt_a_text'] = page_text_list[0]
                page['opt_b_text'] = page_text_list[1]
                if len(page_text_list) > 2:
                    page['other_text'] = str(page_text_list[2:])

        # Get list of option image-URLs
        page_images = us.get_html_from_soup(soup=soup, selector="img")
        page_image_list = []
        if len(page_images) > 0:
            for image in page_images:
                if 'alt' not in image.attrs:
                    page_image_list.append(base_url + image['src'])
            if len(page_image_list) > 0:
                page['opt_a_img'] = page_image_list[0]
                page['opt_b_img'] = page_image_list[1]
                if len(page_image_list) > 2:
                    page['other_images'] = ' | '.join(page_image_list[2:])

    
    else:

        # # test batch
        # if run_count > 10: run_count = "stop"

        # Get Match-page-specific fields

        # Switch page-type
        page['page_type'] = 'Match-page'

        # Add match-taxon
        page['match_taxon'] = us.get_text_from_soup(soup, 'td i')

        if us.get_text_from_soup(soup, 'h1[id=species]') is not None:
            page['match_taxon'] = us.get_text_from_soup(soup, 'h1[id=species]')
            print(page['match_taxon'])

        author = us.get_text_from_soup(soup, 'p[id=zero_margin]')
        print(author)
        if author is not None:
            page['match_taxon'] += f' {author}'

        # Add common name
        td_tags = us.get_text_from_soup(soup, 'td')
        if len(td_tags) > 0:
            for td in td_tags:
                if re.match('Kielelezo chako kinalingana', td.text) is not None:
                    common_name = re.sub(r'Kielelezo chako kinalingana.+\n(.+\n)+(.+)\n*', r'\2', td.text)
                    page['match_common'] = common_name
                    if us.get_text_from_soup(soup, 'h3') is not None and common_name is None:
                        page['match_common'] = us.get_text_from_soup(soup, 'h3')

        # Add images
        page_images = us.get_html_from_soup(soup=soup, selector="img")
        page_image_list = []
        if len(page_images) > 0:
            for image in page_images:
                if 'alt' not in image.attrs:
                    page_image_list.append(base_url + image['src'])
            if len(page_image_list) > 0:
                page['other_images'] = ' | '.join(page_image_list)

        # Get Match-page Text:
        page_text_chunks = us.get_html_from_soup(soup=soup, selector="td")
        page_text_list = []
        if len(page_text_chunks) > 0:
            for chunk in page_text_chunks:
                if 'width' in chunk.attrs:
                    if chunk['width'] == '200':
                        page_text_list.append(chunk.text)
            if len(page_text_list) > 0:
                page['other_text'] = str(page_text_list)

        # Get list of Match-page image-URLs
        page_images = us.get_html_from_soup(soup=soup, selector="img")
        page_image_list = []
        if len(page_images) > 0:
            for image in page_images:
                if 'alt' not in image.attrs:
                    page_image_list.append(base_url + image['src'])
            if len(page_image_list) > 0:
                page['other_images'] = ' | '.join(page_image_list)


    # Get Image credits
    page_image_credits = us.get_html_from_soup(soup=soup, selector="font")

    page_credit_list = []

    for credit in page_image_credits:
        if 'size' in credit.attrs:
            if credit['size'] == '2':
                page_credit_list.append(credit.text)

    if len(page_credit_list) > 0:
        page['image_credits'] = ' | '.join(page_credit_list)


    print(page)
    output_list.append(page)

    return run_count


def main():
    '''main function'''

    config = setup.get_config()

    # Set up command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("start_url", help="top level URL to use as starting point")
    parser.add_argument("output_path", help="Output path (with trailing '/')")
    args = parser.parse_args()

    # First, we need to get all of the URLs we need to scrape
    start_url = args.start_url
    
    output_list = []

    run_count = 0

    get_child_urls(start_url, output_list, config['BASE_URL'], run_count)
    
    # Check if dir exists, and if not, make it
    output_path = args.output_path

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    date_suffix = re.sub(r'\-|\s*|\:|\..*', '', str(date.today()))

    with open(f"{output_path}scraped_skull_key_Swa_{date_suffix}.csv", encoding='utf-8', mode='w') as scraped_urls:
        col_names = list(output_list[0].keys())
        print(col_names)
        write = csv.DictWriter(f=scraped_urls, fieldnames=col_names)
        write.writeheader()
        write.writerows(output_list)


if __name__ == '__main__':
    main()