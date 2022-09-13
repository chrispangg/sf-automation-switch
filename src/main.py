import os
import subprocess
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce
import math

#Operation Toggles
disableAutomation = False
enableAutomation = False

#env variables
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

#Setup Shell Org
orgInit = subprocess.check_call("OrgInit.sh '%s'" % org_alias, stderr=subprocess.PIPE, text=True, shell=True)
print(orgInit.stderr)



def disableValidationRules():
    return None

def disableApexTriggers():
    return None

def disableFlows():
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
                "allOrNone":True,
                "compositeRequest": []
            }

    print("Job Completed!")

    with open('result.json', 'w') as outfile: 
        outfile.write(json.dumps(res, indent=2))
