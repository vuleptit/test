from xml.etree import ElementTree

# find alert config by alert name
def find_alert_config(element_tree: ElementTree, alert_name: str):
    print(element_tree)
    print(element_tree.getroot())
    alert_setting = element_tree.find(alert_name)
    settings = dict()
    for config in alert_setting:
        settings.update({config.tag: config.text})
    return settings

# find alert config attribute
def find_all_alert_config_attributes(element_tree: ElementTree, alert_name: str,alert_config: str, alert_attr: str):
    setting = element_tree.find(alert_name)
    setting_config = setting.find(alert_config)
    setting_config_attribute = setting_config.attrib[alert_attr]
    return setting_config_attribute