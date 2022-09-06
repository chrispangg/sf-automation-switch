import os
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce
import math

#login details
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

#get Flow state to return from OriginalFlowState
with open('OriginalFlowState.json') as outfile:
    data = json.load(outfile)

print("Total flows: " + str(len(data['records'])) + " Total Batches: " + str(math.ceil(len(data['records'])/25)))

res = []
# turnning all flows and procsses back on
payload = {
    "allOrNone":False,
    "compositeRequest": []
}

batchCounter = 0
for i, flow in enumerate(data['records']):
    body = {
        "method":"PATCH",
        "body":{
            "Metadata":{
                "activeVersionNumber": flow["ActiveVersion"]["VersionNumber"]
                },
            },
            "url": flow["attributes"]["url"],
            "referenceId": flow["DeveloperName"]
    }
    payload['compositeRequest'].append(body)

    if len(payload['compositeRequest']) == 25 or i == len(data['records']) - 1:
        callback = sf.toolingexecute('composite/', data=payload, method="POST")
        print("batch " + batchCounter + " completed")
        batchCounter += 1
        res.append(callback)
        payload = {
             "allOrNone":True,
             "compositeRequest": []
        }

print("Job Completed!")

with open('result.json', 'w') as outfile: 
    outfile.write(json.dumps(res, indent=2))

# try:
#     print("Turnning on " + flow['DeveloperName'] + " " + flow['Id'])
    # result = sf.toolingexecute('sobjects/FlowDefinition/' + flow['Id'], method = "PATCH", data=payload)
# except Exception as e: 
#     print(e)
# print("successful")
# print('completed')


# flows = []
# for comp in data['records']:
#     flowAttributes = Attributes(
#         comp['attributes']['type'], 
#         comp['attributes']['url'])

#     flowActiveVersionAttributes = Attributes(
#         comp['ActiveVersion']['attributes']['type'], 
#         comp['ActiveVersion']['attributes']['url'])

#     flowActiveVersion = Version(
#         flowActiveVersionAttributes,
#         comp['ActiveVersion']['VersionNumber'])

#     flowLatestVersionAttributes = Attributes(
#         comp['LatestVersion']['attributes']['type'], 
#         comp['LatestVersion']['attributes']['url'])

#     flowLatestVersion = Version(
#         flowLatestVersionAttributes,
#         comp['LatestVersion']['VersionNumber'])

#     flow = Flow(
#         flowAttributes,
#         comp['Id'],
#         flowActiveVersion,
#         flowLatestVersion,
#         comp['DeveloperName']
#     )
#     flows.append(flow)

