import json
import jmespath

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
        
def get_user_id(filename):
    with open(filename, 'w') as json_file:
        data = json.load(json_file)
        user_id = jmespath.search('members[1].id', data)
        return user_id