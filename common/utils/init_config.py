from xml.etree import ElementTree
import xml.etree.ElementTree as ET
from business_rules.redis.connection import redis as rd
from sys import exc_info
from os.path import dirname, join, abspath
from common.const import XML_CONFIG_FILE_NAME, ALERT_CONFIG_OBJ
import pickle

# get xml configration in a python dict
def get_configuration_dict():
    root_dir = dirname(dirname(dirname(abspath(__file__))))
    xml_file = join(root_dir, XML_CONFIG_FILE_NAME)
    config_xml = ET.parse(xml_file)
    configs = config_xml.getroot()
    alert = dict()
    for al in configs:
        attr = dict()
        for at in al:
            attr.update({at.tag: at.text})
        alert.update({al.tag: attr})
    return alert

# save configuration into redis
async def save_configuration():
    try:
        alert_dict = get_configuration_dict()
        await rd.set(ALERT_CONFIG_OBJ, pickle.dumps(alert_dict))
    except Exception as ex:
        print(exc_info())

