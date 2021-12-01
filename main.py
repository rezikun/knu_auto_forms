from __future__ import print_function

import json
import pickle
from creator import *
from uni_data import *

def save_ids(filename, form_ids: list):
    with open(filename, 'wb') as form_ids_file:
        pickle.dump(form_ids, form_ids_file)


def retrieve_responses(ids_filename, response_folder):
    with open(ids_filename, 'rb') as form_ids_file:
        form_ids = pickle.load(form_ids_file)
    afc = AutomatedFormCreator()
    for form_id in form_ids:
        with open(f"{response_folder}/{form_id}.json", "w", encoding='utf8') as response_file:
            json.dump(afc.retrieve_form_responses(form_id), response_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    print("Choose an operation:")
    print("Pull groups data: 1")
    print("Create forms: 2")
    print("Retrieve responses: 3")
    print("Form links: 4")
    print("Exit: 5")
    while(True):
        choice = input()
        if choice == '1':
            print("Enter a filename to cache the data:")
            filename = input()
            data = UniversityData()
            with open(filename, 'wb') as uni_file:
                pickle.dump(data, uni_file)
            print("Done.")
        elif choice == '2':
            print("Enter groups data cache filename:")
            cache_filename = input()
            with open(cache_filename, 'rb') as uni_file:
                data = pickle.load(uni_file)
            print("Enter a filename to store form ids:")
            filename = input()
            print("Enter filename for mapping:")
            mapping_filename = input()
            creator = AutomatedFormCreator()
            ids, ids_to_groups = creator.create_forms_for_groups(data)
            save_ids(filename, ids)
            with open(mapping_filename, "w", encoding='utf8') as response_file:
                json.dump(ids_to_groups, response_file, ensure_ascii=False, indent=4)
            print("Done.")
        elif choice == '3':
            print("Enter form ids filename:")
            form_ids_filename = input()
            print("Enter a folder name to store the responses in:")
            folder = input()
            retrieve_responses(form_ids_filename, folder)
            print("Done.")
        elif choice == '4':
            print("Enter mapping filename")
            mapping_filename = input()
            with open(mapping_filename, "r", encoding='utf8') as mapping_file:
                mapping_content = json.load(mapping_file)
            links = dict()
            for form_id in mapping_content:
                links[mapping_content[form_id]] = f"https://docs.google.com/forms/d/{form_id}"
            with open("links.json", "w", encoding='utf8') as links_file:
                json.dump(links, links_file, ensure_ascii=False, indent=4)
            print("Done.")
        elif choice == '5':
            break
        else:
            print("Wrong operation.")
