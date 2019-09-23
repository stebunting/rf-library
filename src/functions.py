import requests
import xml.etree.ElementTree
import config

# Function to check for updates
def check_for_updates():
    try:
        r = requests.get(config.APPLICATION_UPDATE_XML_LOCATION)
        update_connection = True
    except requests.exceptions.ConnectionError:
        update_connection = False

    if update_connection:
        root = xml.etree.ElementTree.fromstring(r.text)
        latest = root[0][0].text
        uri = root[0][2].text
        if latest == config.APPLICATION_VERSION:
            return None
        else:
            return {
            	'version': latest,
            	'uri': uri}
    else:
        raise ConnectionError