# tanzanian-mammal-scraper
A set of scrapers to pull data/media from http://archive.fieldmuseum.org/tanzania, and output a CSV that is semi-ready for EMu-import.  Some parsing may be required.

-----

## How to scrape a dichotomous key:

Run `python3 scrape_key.py [starter-URL] [path/where/output/should/go/]`

For example, to scrape the Skull Key, start from its 'general' page:

`python3 scrape_key.py "http://archive.fieldmuseum.org/tanzania/SkullKey.asp?ID=2" output/`

#### Key-scraper output CSV fields:

- order = original URL-order, if needed
- url = original url
- page_type = "Option-page" for pages with dichotomous options/branches, or "Match-page" for matched/id'ed species-detail pages
- opt_a_link = "Option A" URL, a child of the current 'url'
- opt_a_img = "Option A" image, if any
- opt_a_text = "Option A" text, related to type/trait descriptions
- opt_b_link = "Option B" URL, a child of the current 'url'
- opt_b_img = "Option B" image, if any
- opt_b_text = "Option B" text, related to type/trait descriptions
- other_images = Images from match-pages (or if more than 2 pages occur on option-pages)
- taxon = Genus name from Match-page
- match_text = body-text of a Match-page

-----

## How to scrape the species-list page:

Run `python3 scrape_species.py [species list URL] [path/where/output/should/go/]`

For example, to start from the "general" page of the Skull Key:

`python3 scrape_species.py "http://archive.fieldmuseum.org/tanzania/Species_Home.asp" output/`

# EMu Records
2024-July: English records are imported to EMu

#### Multimedia
- Group name: TAN website images (496)

#### Narratives 
- Group name: TAN Skin Key Options and Matches (535)
- To do:
  - corresponding Swahili key pages
  - Skull Key pages




