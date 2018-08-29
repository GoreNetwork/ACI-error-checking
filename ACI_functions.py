import json
import requests
import os
from xml.etree import ElementTree as et
from pprint import pprint
from getpass import getpass

def get_token(username, password, base_url):

    requests.packages.urllib3.disable_warnings()  # Disable warning message

    # create credentials structure
    name_pwd = {'aaaUser': {'attributes': {'name': username, 'pwd': password}}}
    json_credentials = json.dumps(name_pwd)
    # print (1)

    # log in to API
    login_url = base_url + 'aaaLogin.json'
    post_response = requests.post(login_url, data=json_credentials, verify=False)

    # pprint (post_response)

    # get token from login response structure
    auth = json.loads(post_response.text)
    # pprint (auth)
    login_attributes = auth['imdata'][0]['aaaLogin']['attributes']
    auth_token = login_attributes['token']
    # pprint (auth_token)
    # create cookie array from token
    cookies = {}
    cookies['APIC-Cookie'] = auth_token
    return cookies




def pull_brige_domain_data (cookies,base_url):
    bridge_domains = []
    # read a sensor, incorporating token in request
    sensor_url = base_url + 'node/class/fvBD.xml?'
    #root = et.parse(urllib.urlopen(sensor_url)).getroot()
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint (root.attrib)
    for each in root:
        #pprint (each.attrib)
        bridge_domains.append(each.attrib)
    return (bridge_domains)

def pull_vlan_data (cookies,base_url):
    vlans = []
    sensor_url = base_url + 'node/class/fvAEPg.xml?'
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    for each in root:
        vlans.append(each.attrib)
    return (vlans)

def pull_vlan_interface_data(cookies,base_url,interface_data):
    attributes = []
    sensor_url = base_url + 'node/mo/'
    sensor_url = sensor_url+ interface_data+".xml?query-target=self"
    #pprint (sensor_url)
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    for each in root:
        #pprint (each.attrib)
        #pprint(each)
        attributes.append(each.attrib)
    return (attributes)

#Pull all interfaces
def pull_path_attributes (cookies,base_url):
    attributes = []
    sensor_url = base_url + 'node/class/fvRsPathAtt.xml?'
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint (root.attrib)
    for each in root:
        #pprint (each.attrib)
        #pprint(each)
        attributes.append(each.attrib)
    return (attributes)

def pull_vlan_interface_data (cookies,base_url,dn):

    vlan_interface_data = []
    #sensor_url = base_url + 'node/class/fvRsPathAtt.xml?'
    sensor_url = base_url +"node/mo/"
    sensor_url = sensor_url + dn
    sensor_url = sensor_url +".xml?query-target=children&target-subtree-class=fvRsPathAtt"
   # pprint (sensor_url)
    # root = et.parse(urllib.urlopen(sensor_url)).getroot()
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint(root.attrib)
    for each in root:
        #pprint(each.attrib)
       # pprint(each)
        vlan_interface_data.append(each.attrib)

    return (vlan_interface_data)

def pull_crc_errors(cookies, base_url):
    ports = []
    #sensor_url = base_url+ 'node/class/rmonEtherStats.xml?'
    sensor_url = base_url+ 'node/class/rmonEtherStats.xml?query-target-filter=and(gt(rmonEtherStats.cRCAlignErrors,"0"))'
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint(root.attrib)

    for each in root:
        #pprint(each.attrib)
       # pprint(each)
        ports.append(each.attrib)

    return ports

def pull_switches(cookies,base_url):
    all_data = []
    sensor_url = base_url + "node/mo/topology/pod-1.xml?query-target=children"
    #pprint (sensor_url)
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    for each in root:
        all_data.append(each.attrib)
    return (all_data)

def pull_all_switch_SNs(ACI_sites,username,password):
    all_node_IDs = {}
    for ACI_site in ACI_sites:
        node_dict = {}
        dc = ACI_site[0]
        base_url = ACI_site[1]
        cookies = get_token(username,password,base_url)
        switches = pull_switches(cookies,base_url)
        for switch in switches:
            if 'nodeId' in switch:
                node = switch['nodeId']
                node_data = pull_node_data(cookies, base_url,node)[0]
                node_sn = node_data['ser']
            # print ('node ',node)
                #print ('node_sn ',node_sn)
                all_node_IDs[node] = node_sn

                #pprint (node_data)
    return all_node_IDs


def pull_node_data(cookies, base_url,node):
    ports = []
    url_extra = 'node/mo/topology/pod-1/node-{}/sys/ch.xml?query-target=self'.format(node)
    #sensor_url = base_url+ 'node/class/rmonEtherStats.xml?'
    sensor_url = base_url+ url_extra
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint(root.attrib)

    for each in root:
        #pprint(each.attrib)
       # pprint(each)
        ports.append(each.attrib)

    return ports


def pull_lldp_data(cookies, base_url):
    lldp_data = []
    url_extra = 'node/class/lldpAdjEp.xml?'
    #sensor_url = base_url+ 'node/class/rmonEtherStats.xml?'
    sensor_url = base_url+ url_extra
    get_response = requests.get(sensor_url, cookies=cookies, verify=False)
    root = et.fromstring(get_response.content)
    #pprint(root.attrib)

    for each in root:
        #pprint(each.attrib)
       # pprint(each)
        lldp_data.append(each.attrib)

    return lldp_data

#In a lot of data from the ACI there is a dn feild.  This pulls the port number from that if there is one
def find_port_from_dn_data(dn_data):
    dn_data = dn_data.split('[')
    for dn_part in dn_data:
        dn_part = dn_part.split(']')
        for tiny_part in dn_part:
            if 'eth' in tiny_part:
                port = tiny_part
                return port
            if 'pod' in tiny_part:
                continue
            if 'po' in tiny_part:
                port = tiny_part
                return port

#In a lot of data from the ACI there is a dn feild.  This pulls the node number from that if there is one (Output is node-#)
def find_node_from_dn_data(dn_data):
    dn_data = dn_data.split('/')
    for dn_part in dn_data:
        if 'node' in dn_part:
            node = dn_part
            return node


def build_lldp_dict(all_lldp_entries):
    lldp_dict = {}
    for lldp_entry in all_lldp_entries:
        #pprint (lldp_entry)
        node = find_node_from_dn_data(lldp_entry['dn'])
        port = find_port_from_dn_data(lldp_entry['dn'])
        if node not in lldp_dict:
            lldp_dict[node] = {}
        if  port not in lldp_dict[node]:
            lldp_dict[node][port] = []
        tmp_dic = {}
        remote_node = ''
        remote_port = ''
        try:
            remote_port = find_port_from_dn_data(lldp_entry['portDesc'])
            remote_node = find_node_from_dn_data(lldp_entry['sysDesc'])
        except:
            pass
        tmp_dic['node'] = remote_node
        tmp_dic['port'] = remote_port
        tmp_dic['sysDesc'] = lldp_entry['sysDesc']
        tmp_dic['sysName'] = lldp_entry['sysName']
        lldp_dict[node][port].append(tmp_dic)
    return(lldp_dict)



ACI_sites = [
   # ['DC1_name','https://DC1-apic.fake-company.com/api/'],
   # ['DC2_name,','https://DC2-apic.fake-company.com/api/'],
    ['DC3_name','https://10.1.96.5/api/'],
]
#This might be diffrent, it's how you would login to the switches
username = 'apic#Tacacs_ACI\\'+input("Username: ")

#pprint (username)
password = getpass()