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

#get Flow state to return
with open('ReturnState.json') as outfile:
    data = json.load(outfile)

flows = []
for comp in data['records']:
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
        flowActiveVersion,
        flowLatestVersion,
        comp['DeveloperName']
    )
    flows.append(flow)

# turnning all flows and procsses back on
for flow in flows:
    payload = {
        'Metadata': {
            'activeVersionNumber': flow.active_version.version_number
        }
    }
    try:
        print("Turnning on " + flow.developer_name + " " + flow.id)
        result = sf.toolingexecute('sobjects/FlowDefinition/' + flow.id, method = "PATCH", data=payload)
    except Exception as e: 
        print(e)
    print("successful")
print('completed')