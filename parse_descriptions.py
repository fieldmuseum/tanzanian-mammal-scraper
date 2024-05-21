'''Parse raw descriptions to etaxonomy Description tab fields'''

from datetime import datetime
import os, re
import utils.csv as uc

def parse_descriptions(raw:dict) -> dict:
    '''Parse the raw scraped description text for etaxonomy fields in the Description table'''

    prepped = {}

    prepped['irn'] = raw['irn']
    print(prepped['irn'])

    type_desc_fixed = re.sub(
        'Type Description:',
        'Type-Desc:',
        raw['descrip_text_raw']
        )

    labels = [
        'Type-Desc:',
        'Description:',
        'Type Locality:',
        'Distribution:',
        'Key References:',
        'Key Reference:',
        'Comparisons:',
        'Measurements:',
        'Figure'
    ]

    # Find each description-label in the raw-text, and insert pipes into raw text to make parsing easier
    raw_description_text = re.sub(
        rf'({"|".join(labels)})',
        # r'(Type-Desc\:|Description\:|Type Locality\:|Distribution\:|Key References*\:|Comparisons*\:|Measurements*\:|Figure)',
        ' | \g<1>',
        type_desc_fixed
        )
    
    raw_descrip_list = raw_description_text.split(' | ')

    if str(raw['irn']) == '313512':
        print(f'raw_description_text    ==    ==    {raw_description_text}')

    # Setup lists to group un-found labels
    found_labels = []
    pad_empty_labels = []

    for label in labels:
        if label not in ['Figure']:  # , 'Measurements:'
            if len(re.findall(label, raw_description_text)) > 0:
                found_labels.append(label)
            else:
                pad_empty_labels.append(label)

    i = 1

    for label in found_labels:

        for row in raw_descrip_list:
            if len(re.findall(label, row)) > 0:

                label_column = f"DesLabel0(+ group='{i}')"
                text_column = f"DesDescription0(+ group='{i}')"
                biblio_column = f"DesBiblioRef0(+ group='{i}').irn"

                prep_label = re.sub(r'\:', '', label)
                if label == 'Type-Desc:':
                    prep_label = 'Type Description'
                
                prep_row = re.sub(label, '', row).strip()
                if label == 'Measurements:':
                    prep_row = re.sub(r'(\S+)([A-Z])', 
                                      '''\g<1>
\g<2>''', 
                                      prep_row)

                if label == 'Key Reference:':
                    prep_label = 'Key References'
                    prep_row = re.sub(r'(\.)(\d)',
                                      '''\g<1> 
\g<2>''', 
                                      prep_row)

                prepped[label_column] = prep_label
                prepped[text_column] = prep_row
                prepped[biblio_column] = 41852

                if str(raw['irn']) == '313512':
                    print(f'prepped description_text    ==  {prep_label}  ==  {prep_row}')

                i += 1
        
    j = i
    if len(pad_empty_labels) > 0:
        for pad in pad_empty_labels:
            pad_label_column = f"DesLabel0(+ group='{j}')"
            pad_text_column = f"DesDescription0(+ group='{j}')"
            pad_biblio_column = f"DesBiblioRef0(+ group='{j}').irn"

            prepped[pad_label_column] = None
            prepped[pad_text_column] = None
            prepped[pad_biblio_column] = None
            j += 1

    return prepped


def main():
    '''main function'''

    tax_descriptions = uc.rows("output/scraped_taxon_20221024_irns.csv")

    prepped_descriptions = []

    for taxon_row in tax_descriptions:
        prepped_row = parse_descriptions(taxon_row)

        if prepped_row not in prepped_descriptions:
            prepped_descriptions.append(prepped_row)
    

    if len(prepped_descriptions) > 0:
        '''output prepped rows'''

        date_stamp = re.sub(r'\s|\:|\..+', '', f'{datetime.now()}')
        
        uc.output_list_of_dict_to_csv(
            list_of_dict = prepped_descriptions,
            csv_fieldnames = prepped_descriptions[0].keys(),
            output_path = "output",
            output_file = f"parsed_taxa_{date_stamp}.csv")


if __name__ == '__main__':
    main()