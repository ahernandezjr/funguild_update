import requests
import json
import csv
from excel2json import convert_from_file


# Gets request type and formats to json or returns None for empty json
def get_query_json(request):
    response = requests.get(request)
    if response.text == '0 results':
        return None
    return json.loads(response.text)


def search_key(taxon, key, dump_list, QUERY_URL):
    # Assign name
    taxon_name = taxon['taxon']
    if ((taxon_name == '' or taxon_name == False) and taxon["CORRECT_taxon"] != ''):
        taxon_name = taxon["CORRECT_taxon"]

    # Check if the 'key' should be used for searching or not
    if (taxon[key] == 'NA' or taxon[key] == '' or taxon[key] == False):
        print(taxon_name + ': ' + key + ' unable to be used.')

    else:
        # Check if multiple IDs, then maybe more than 1 query
        key_list = taxon[key]
        if isinstance(key_list, float):
            key_list = int(key_list)
        
        if (isinstance(key_list, str) and key_list.count(',') > 0):
            # Converts from an R list to a python list
            key_list = key_list.split('(')[1].split(')')[0].split(',')

            # Iterate through created key_list
            for id in key_list:
                query_json = get_query_json(QUERY_URL + str(id))
                if isinstance(query_json, list):
                    for item in query_json:
                        # Empty query
                        if (query_json == None):
                            print(taxon_name + ' / ' + str(id) + ': no associated query.')
                        # If value to key is a valid status
                        elif verify_status(item['taxonomicStatus']):
                            dump_list.append([taxon_name, item['otherID'], id, item['taxonomicStatus']])
                else:
                    # Empty query
                    if (query_json == None):
                        print(taxon_name + ' / ' + str(id) + ': no associated query.')
                    # If value to key is a valid status
                    elif verify_status(query_json['taxonomicStatus']):
                        dump_list.append([taxon_name, query_json['otherID'], id, query_json['taxonomicStatus']])

        # If 1 ID, do single query
        else:
            query_json = get_query_json(QUERY_URL + str(key_list))
            # Checks if multiple results for id
            if isinstance(query_json, list):
                for item in query_json:
                    # Empty query
                    if (query_json == None):
                        print(taxon_name + ' / ' + str(key_list) + ': no associated query.')
                    # If value to key is a valid status
                    elif verify_status(item['taxonomicStatus']):
                        dump_list.append([taxon_name, item['otherID'], key_list, item['taxonomicStatus']])
            # Only 1 results for id
            else:
                # Empty query
                if (query_json == None):
                    print(taxon_name + ' / ' + str(key_list) + ': no associated query.')
                # If value to key is a valid status
                elif verify_status(query_json['taxonomicStatus']):
                    dump_list.append([taxon_name, query_json['otherID'], key_list, query_json['taxonomicStatus']])


# Verifies if the 'status' is in the accepted taxonomy
# Returns a True or False
def verify_status(status):
    # Loop through all accepted taxonomy
    for accepted in ACCEPTED_TAXONOMY:
        # Return True if in the tuple
        if (status.casefold() == accepted.casefold()):
            return True

    # Return False if not in tuple
    return False


# URLs for querying using GUID or MycoBank Nymber
GUID_QUERY_URL = 'https://www.mycoportal.org/fdex/services/api/query.php?qField=otherID&qText='
MBNUM_QUERY_URL = 'https://www.mycoportal.org/fdex/services/api/query.php?qField=mbNumber&qText='

# List of accepted names
ACCEPTED_TAXONOMY = ('conserved', 'legitimate', 'assumed legitimate')

# Variables to be used
json_data = []
final_matches = []

# Create json file from excel and load json
excel_import_file = 'FuNGuild_Need_Help.xls'
convert_from_file(excel_import_file)

with open('Sheet1.json') as json_file:
    json_data = json.load(json_file)

i = 1

# Begins iterations of every json object in json file
for taxon in json_data:
    print('Starting job ' + str(i) + ':')

    # Accepted matches are put into a list for final checking
    accepted_matches = []

    # Ignore completed tag items
    if taxon['completed'] == 'x':
        print(taxon['taxon'] + ': already completed.')
        i += 1
        continue
    
    # 1 --- First, attempt GUID
    search_key(taxon, 'guid', accepted_matches, GUID_QUERY_URL)

    # # 2 --- Then, attempt with MycoBank Number
    search_key(taxon, 'mbNumber', accepted_matches, MBNUM_QUERY_URL)

    if accepted_matches:
        final_match = accepted_matches[0]

        for item in accepted_matches:
            if ACCEPTED_TAXONOMY.index(item[3].lower()) < ACCEPTED_TAXONOMY.index(final_match[3].lower()):
                final_match = item

        final_matches.append(final_match)

    i += 1

with open('final_matches.csv', 'w') as f:
    f.write('taxon,fdexOtherID,queryID,otherIDStatus\n')
    wr = csv.writer(f)
    wr.writerows(final_matches)
