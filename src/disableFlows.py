import os
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce
from models import Flow, Attributes, Version

#login details
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

#get original flow states
result = sf.toolingexecute('query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition+Where+ActiveVersion.VersionNumber!=null')
jsonify = json.dumps(result, indent=2)
with open('originalFlowState.json', 'w') as outfile: 
    outfile.write(jsonify)

flows = []
for comp in result['records']:
    flowAttributes = Attributes(
        comp['attributes']['type'], 
        comp['attributes']['url'])

    flowActiveVersionAttributes = Attributes(
        comp['ActiveVersion']['attributes']['type'], 
        comp['ActiveVersion']['attributes']['url'])

    flowActiveVersion = Version(
        flowActiveVersionAttributes,
        comp['ActiveVersion']['VersionNumber'])

    flowLatestVersionAttributes = Attributes(
        comp['LatestVersion']['attributes']['type'], 
        comp['LatestVersion']['attributes']['url'])

    flowLatestVersion = Version(
        flowLatestVersionAttributes,
        comp['LatestVersion']['VersionNumber'])

    flow = Flow(
        flowAttributes,
        comp['Id'],
        0,
        flowLatestVersion,
        comp['DeveloperName']
    )
    flows.append(flow)

payload = {
        'Metadata': {
            'activeVersionNumber': 0
        }
    }
for flow in flows:
    try: 
        print("Turning off " + flow.developer_name + " " + flow.id)
        result = sf.toolingexecute('sobjects/FlowDefinition/' + flow.id, method = "PATCH", data=payload)
    except Exception as e: 
        print(e)
    print("successful")

print("completed")
        





# for comp in result['records']:

