# ACI-error-checking
Connects to the ACI's API finds ports with an error # higher than what is listed, then pulls LLDP data down and reports on what it is seeing.
Then it will email the results to a list of people who should resolve the issues.

The email should look like this:

----------------------------
Data_Center: (DC_NAME)
Device with errors:
    Node: node-15
    SN: FAKESN1 
    Port:eth1/1
    Error Count:188
                
Neighbor Device:
    Name: Fake_name.fake-company.com
    Desc: topology/pod-1/node-16
    Node: node-16
    SN: FAKESN2
    Port: eth1/50
----------------------------
LLDP Neighbor not found for this entry
Device with errors:
    Data_Center: (DC_NAME)
    Node: node-15
    SN: FAKESN3
    Port:eth101/1/6
    Error Count:1131
----------------------------
