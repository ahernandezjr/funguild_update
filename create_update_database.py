import requests
import json
from excel2json import convert_from_file


# Gets request type and formats to json or returns None for empty json
def get_query_json(request):
    response = requests.get(request)
    if response.text == '0 results':
        return None
    return json.loads(response.text)

# Verifies if the 'status' is in the accepted taxonomy
# Returns a True or False
def verify_status(status):
    # Loop through all accepted taxonomy
    for accepted in ACCEPTED_TAXONOMY:
        # Return True if in the tuple
        if (status == accepted):
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


# Create json file from excel and load json
excel_import_file = 'FuNGuild_Need_Help.xls'
convert_from_file(excel_import_file)

with open('Sheet1.json') as json_file:
    json_data = json.load(json_file)


# Begins iterations of every json object in json file
for taxon in json_data:
    # Accepted matches are put into a list for final checking
    accepted_matches = []

    # Assign name
    taxon_name = taxon['taxon']
    if ((taxon_name != False or taxon_name != '') and taxon["CORRECT_taxon"] != ''):
        taxon_name = taxon["CORRECT_taxon"]

    # Ignore completed tag items
    if taxon['completed'] == 'x':
        print(taxon_name + ': already completed.')
        continue
    
    
    print('Starting: ' + taxon_name)

    # 1 --- First, attempt GUID
    if (taxon['guid'] != False or taxon['guid'] != 'NA' or taxon['guid'] != ''):
        # Check if multiple GUIDs, then maybe more than 1 query
        guid_list = taxon['guid']
        if guid_list.count(',') > 0:
            # Converts from an R list to a python list
            guid_list = guid_list.split('(')[1].split(')')[0].split(',')

            # Iterate through created GUID list
            for guid in guid_list:
                query_json = get_query_json(GUID_QUERY_URL + guid)
                if isinstance(query_json, list):
                    for item in query_json:
                        print(taxon_name + ' / ' + taxon['guid'] + ': no associated query.')
                        if verify_status(query_json['taxonomicStatus']):
                            accepted_matches.append(guid)
                else:
                    if (query_json == None):
                        print(taxon_name + ' / ' + taxon['guid'] + ': no associated query.')
                        if verify_status(query_json['taxonomicStatus']):
                            accepted_matches.append(guid)

        # If 1 ID, do single query
        else:
            query_json = get_query_json(GUID_QUERY_URL + taxon['guid'])
            if (query_json != None):
                if verify_status(query_json['taxonomicStatus']):
                    accepted_matches.append(taxon['guid'])
            else:
                print(taxon_name + ' / ' + taxon['guid'] + ': no associated query.')



    # # 2 --- Then, attempt with MycoBank Number
    # if (taxon['mbNumber'] != False or taxon['mbNumber'] != 'NA'  or taxon['mbNumber'] != 'NA' or taxon['mbNumber'] != ''):
    #     query_json = get_query_json(MBNUM_QUERY_URL + taxon['mbNumber'].split('.')[0])

    #     if (query_json == None):
    #         print(taxon_name + ' / ' + taxon['mbNumber'] + ': no associated query.')
    #     else:
    #         if verify_status(query_json['taxonomicStatus']):
    #             accepted_matches.append(taxon['mbNumber'])

    # TEST --- First, attempt GUID
    if (taxon['mbNumber'] != False or taxon['mbNumber'] != ''):
        # Check if multiple GUIDs, then maybe more than 1 query
        mbNumber_list = taxon['mbNumber']
        if mbNumber_list.count(',') > 0:
            # Converts from an R list to a python list
            mbNumber_list = mbNumber_list.split('(')[1].split(')')[0].split(',')

            # Iterate through created mbNumber list
            for mbNumber in mbNumber_list:
                query_json = get_query_json(MBNUM_QUERY_URL + guid)
                if (query_json == None):
                    print(taxon_name + ' / ' + taxon['mbNumber'] + ': no associated query.')
                    if verify_status(query_json['taxonomicStatus']):
                        accepted_matches.append(mbNumber)

        # If 1 ID, do single query
        else:
            query_json = get_query_json(MBNUM_QUERY_URL + taxon['guid'])
            if (query_json != None):
                if verify_status(query_json['taxonomicStatus']):
                    accepted_matches.append(taxon['mbNumber'])
            else:
                print(taxon_name + ' / ' + taxon['mbNumber'] + ': no associated query.')
    
