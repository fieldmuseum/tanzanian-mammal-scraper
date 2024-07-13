'''Scraper for Tanzanian Mammals ID Key Images'''

import os, re, time
import utils.csv as uc
import utils.scrape as us
import utils.setup as setup


def get_image_files(
        image_url_list:list = None, 
        output_path:str = None, 
        run_count:int = 1):
    '''given a list of image URLs, retrieve image files'''

    for image_url in image_url_list:

        run_total= len(image_url_list)

        image_filename = re.sub(r'(http.*\://)(.+/)+(.+\..+$)', '\g<3>', image_url)
        image_path = f'{output_path}{image_filename}'

        print(f'row {run_count} / {run_total} -- {image_url} --> {image_path}')

        img_response = us.get_image(url = image_url, local_path=image_path)
        print(img_response)

        run_count += 1

        time.sleep(.5)


def get_image_list(scraped_page_list:list=None) -> list:
    '''given a list of dicts of scraper-output, return list of image URLs'''

    all_images = []

    for row in scraped_page_list:
        opt_a_img = row['opt_a_img'].split('|')
        opt_b_img = row['opt_b_img'].split('|')
        other_images = row['other_images'].split('|')

        image_list_raw = list(set(opt_a_img + opt_b_img + other_images))
        
        for image_raw in image_list_raw:

            image = image_raw.strip()

            if image not in all_images and image not in [None, '']:
                all_images.append(image)
    
    return all_images


def main():
    '''main function'''

    # Set up inputs
    config = setup.get_config()

    # Get image URL list from previous scraper-output
    skull_rows = uc.rows(config['SKULL_KEY_OUTPUT_CSV'])
    skin_rows = uc.rows(config['SKIN_KEY_OUTPUT_CSV'])
    all_rows = skull_rows + skin_rows
    all_images = []

    all_images = get_image_list(all_rows)
    
    print(f'Full image-list length:  {len(all_images)} URLs')


    # # Check if output dir exists, and if not, make it
    output_path = config['IMAGE_OUTPUT_FOLDER']

    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # test smaller set
    all_images = all_images[0:5]

    get_image_files(all_images)


if __name__ == '__main__':
    main()