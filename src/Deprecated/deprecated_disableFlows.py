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

result = sf.toolingexecute('query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition+Where+ActiveVersion.VersionNumber!=null')

jsonify = json.dumps(result, indent=2)
with open('newFlowState.json', 'w') as outfile: 
    outfile.write(jsonify)

print("Total flows: " + str(len(result['records'])) + " Total Batches: " + str(math.ceil(len(result['records'])/25)))

res = []
payload = {
    "allOrNone":False,
    "compositeRequest": []
}
batchCounter = 1
for i, flow in enumerate(result['records']):
    body = {
        "method":"PATCH",
        "body":{
            "Metadata":{
                "activeVersionNumber": 0
                },
            },
            "url": flow["attributes"]["url"],
            "referenceId": flow["DeveloperName"]
        }
    payload['compositeRequest'].append(body)

    if len(payload['compositeRequest']) == 25 or i == len(result['records']) - 1:
        callback = sf.toolingexecute('composite/', data=payload, method="POST")
        print("batch " + str(batchCounter) + " completed")
        batchCounter += 1
        res.append(callback)
        payload = {
             "allOrNone":False,
             "compositeRequest": []
        }

print("Job Completed!")

with open('result.json', 'w') as outfile: 
    outfile.write(json.dumps(res, indent=2))