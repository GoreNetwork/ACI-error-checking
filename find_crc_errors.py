from ACI_functions import *
from pprint import pprint 
import xml.etree.ElementTree as et
import xmltodict, json
import smtplib
from email.message import EmailMessage

data = ''
#How many errors do you want it to ignore before it tells you about it.  
#This is refrenced as if errors > theshold don't ignore it
threshold = 100

def send_email(subject, content):
    sender = 'sender_email@gmail.com'
    recipient = [
                'dhimes@gmail.com',
                ]
    server = 'email_server.fake_company.com'

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP(server)
    s.send_message(msg)
    s.quit()

#Don't think I ended up using this, but not going to delete just in case
def etree_to_dict(t):
    d = {t.tag : map(etree_to_dict, t.iterchildren())}
    d.update(('@' + k, v) for k, v in t.attrib.iteritems())
    d['text'] = t.text
    return d

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

def find_node_from_dn_data(dn_data):
    dn_data = dn_data.split('/')
    for dn_part in dn_data:
        if 'node' in dn_part:
            node = dn_part
            return node

all_data = []
#See ACI_functions for the list of ACIs
for ACI_site in ACI_sites:
    #Data center name, used for human readability
    dc = ACI_site[0]
    #URL to address the ACI
    base_url = ACI_site[1]
    #Login to the ACI
    cookies = get_token(username,password,base_url)
    #Grab the CRC errors
    ports_data = pull_crc_errors(cookies, base_url)
    #Pull the LLDP data
    all_lldp_data = pull_lldp_data(cookies, base_url)
    #Turn the LLDP data into a dict, makes searching for data way easier IMO
    all_lldp_data = build_lldp_dict(all_lldp_data)
    #Grab the serial numbers for all the switches
    sn_data = pull_all_switch_SNs(ACI_sites,username,password)
    #pprint (all_lldp_data)
    for port_data in ports_data:
        dn_data = port_data['dn']
        all_data.append(dn_data)
        #find port
        port = find_port_from_dn_data( dn_data)
        #find node
        node = find_node_from_dn_data( dn_data)
        #Find the CRC errors
        errors = port_data['cRCAlignErrors']
        #If the # of errors isn't higher than the threshold ignore this port
        if int(errors) > threshold:
            tmp_local_node = node.split('-')[1]
            #I suck so some times the node is refrenced as "node-#" and sometimes as #
            local_sn = sn_data[tmp_local_node]
            #This is the string that will be used if an LLDP neighor isn't found, if a neighbor is found this will be over written
            tmp_string = '''
LLDP Neighbor not found for this entry
Device with errors:
    Data_Center: {}
    Node: {}
    SN: {} Port:{}
    Error Count:{}
------------------------------    
'''.format (dc,node,local_sn, port, errors)
            #Try and see if it can find an LLDP neighbor for this node/port, if it can build a new string to go into the email
            try:
                lldp_data = all_lldp_data[node][port]

            
                for lldp_neighbor in lldp_data:
                
                    neighbor_node = lldp_neighbor['node']
                    tmp_neighbor_node = neighbor_node.split('-')[1]
                    neighbor_port = lldp_neighbor['port']
                    neighbor_name = lldp_neighbor['sysName']
                    neighbor_sn = sn_data[tmp_neighbor_node]
                    neighbor_desc = lldp_neighbor['sysDesc']
                    tmp_string = """
Data_Center: {}
Device with errors:
    Node: {}
    SN: {} 
    Port:{}
    Error Count:{}
                
Neighbor Device:
    Name: {}
    Desc: {}
    Node: {}
    SN: {}
    Port: {}
------------------------------
""".format (dc,node,local_sn, port, errors,neighbor_name,neighbor_desc,neighbor_node,neighbor_sn,neighbor_port)
                    data = data + tmp_string
                    #If all that was found add the new string to the email
                    tmp_string = ''
            except:
                #If it wasn't all found add the old string
                data = data+ tmp_string
print(data)
            




#print(data)

#Send an email, subject, and body
send_email("DC Errors Test", data)


            
    
            