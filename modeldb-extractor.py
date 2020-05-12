"""
Get model zip files and metadata from ModelDB.

Robert A. McDougal 2020-05-11

Note: while most models have associated zip files, probably a couple hundred do not.
Those are the "web link to models" (additional information for these models is stored
in attribute 24.)
"""

import requests
import json
import atexit
import base64
import os
import tqdm

zip_dir = 'zips'
try:
    os.makedirs(zip_dir)
except FileExistsError:
    pass

model_ids = [
    item['id']
    for item in requests.get('https://senselab.med.yale.edu/_site/webapi/object.json/?cl=19').json()['objects']
]

all_metadata = {}

# this way even if we control-C, we get something
@atexit.register
def shutdown():
    with open('modeldb-metadata.json', 'w') as f:
        json.dump(all_metadata, f, indent=4)


ignored_attributes = {
    'runprotocols',
    'hide_autolaunch_button',
    'has_modelview',
    'simPFid',
    'hg'
}

for model_id in tqdm.tqdm(model_ids):
    unprocessed_metadata = requests.get(
        f"https://senselab.med.yale.edu/_site/webapi/object.json/{model_id}?woatts=24"
    ).json()
    metadata = {
        'title': unprocessed_metadata['object_name'],
        'id': model_id
    }
    for item in unprocessed_metadata['object_attribute_values']:
        if item['attribute_id'] == 23:
            # the zip file
            with open(os.path.join(zip_dir, f'{model_id}.zip'), 'wb') as f:
                f.write(base64.standard_b64decode(item['value']['file_content']))
        else:
            name = item['attribute_name']
            if name not in ignored_attributes:
                if 'value' in item:
                    value = [item['value']]
                else:
                    value = item['values']
                metadata[name] = value
    all_metadata[model_id] = metadata


