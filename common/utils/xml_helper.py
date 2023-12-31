from xml.etree import ElementTree
# find alert config by alert name
def find_config(element_tree: ElementTree, alert_name: str, alert_config: str):
    alert_setting = element_tree.find(alert_name)
    settings = dict()
    for config in alert_setting:
        settings.update({config.tag: config.text})
    return settings[alert_config]

# find alert config attribute
def find_alert_config_attributes(element_tree: ElementTree, alert_name: str,alert_config: str, alert_attr: str):
    setting = element_tree.find(alert_name)
    setting_config = setting.find(alert_config)
    setting_config_attribute = setting_config.attrib[alert_attr]
    return setting_config_attribute


def find_reset_time(element_tree: ElementTree):
    setting = element_tree.getroot()
    return int(setting.attrib["resettime"])

def get_external_http_endpoint(element_tree: ElementTree):
    setting = element_tree.getroot()
    http_endpoint = setting.find("endpoint")
    return http_endpoint.text
