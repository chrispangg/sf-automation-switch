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

batchCounter = 1
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
        print("batch " + str(batchCounter) + " completed")
        batchCounter += 1
        res.append(callback)
        payload = {
             "allOrNone":True,
             "compositeRequest": []
        }

print("Job Completed!")

with open('result.json', 'w') as outfile: 
    outfile.write(json.dumps(res, indent=2))

