import requests

api_link = 'https://jisho.org/api/v1/search/words?keyword='


def get_translation(source):
    r = requests.get(api_link + source).json()
    if r['data']:
        json = r['data'][0]
        word = json['slug']
        readings = [j['reading'] for j in json['japanese']]
        common = 'is common' if json['is_common'] else 'is not common'
        sense_keys = ['english_definitions', 'parts_of_speech']
        senses = [{key: sense[key] for key in sense_keys} for sense in json['senses']]
        for sense in senses:
            if not sense['parts_of_speech']:
                sense['parts_of_speech'] = ['']
        return word, readings, common, senses
    return None, None, None, None
