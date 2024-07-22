'''Scraper for Tanzanian Mammals ID Key Images'''

import os, re, time
import utils.csv as uc
import utils.scrape as us
import utils.setup as setup
from datetime import datetime, timedelta

def get_time_remaining(start, end, img_times, run_total, run_count, sleep_time):
    '''estimate remaining time based on current average time'''

    img_time = end - start 
    img_times.append(img_time)

    img_time_ave = sum(img_times, timedelta(0,0,0)) / len(img_times)
    avg_remain_time = (run_total - run_count) * (img_time_ave + timedelta(seconds=sleep_time))

    return avg_remain_time


def get_image_files(
        image_url_list:list = None, 
        output_path:str = './', 
        run_count:int = 1,
        sleep_time = 0.25):
    '''given a list of image URLs, retrieve image files'''

    img_times = []
    run_total = len(image_url_list)

    for image_url in image_url_list:

        image_filename = re.sub(r'(http.*\://)(.+/)+(.+\..+$)', '\g<3>', image_url)

        image_path = f'{output_path}{image_filename}'

        if len(re.findall(r'^http', image_filename)) > 0:

            print(f'Skipping row {run_count} -- mangled url {image_url} or local path: {image_path}')
        
        else:

            print(f'row {run_count} / {run_total} | {image_url} -> {image_path}')

            img_start = datetime.now()
            us.get_image(url = image_url, local_path=image_path)
            img_end = datetime.now()

            remain_time = get_time_remaining(img_start, img_end, img_times, run_total, run_count, sleep_time)

            print(f'remaining: {remain_time}')

            time.sleep(sleep_time)

        run_count += 1


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

    # # test smaller set
    # all_images = all_images[734:]

    start = datetime.now()
    print(start)

    get_image_files(all_images, output_path=output_path)

    end = datetime.now()
    print(f'{end} -- total run-time = {end-start}')

if __name__ == '__main__':
    main()