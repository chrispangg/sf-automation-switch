import os
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce

#Environment Variables
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

# get names of active validation rules and save them to a json file

with open('ValidationRulesWithMetadata.json', 'r') as readfile:
    validationRules = json.load(readfile)

# Create payloads
payloads = [] #25 records per payload
payload = {
    "allOrNone":False,
    "compositeRequest": []
}
for i, rule in enumerate(validationRules):
    body = {
        "method":"PATCH",
            "body":{
                "Metadata": {
                    "description": rule['Metadata']['description'],
                    "errorConditionFormula": rule['Metadata']['errorConditionFormula'],
                    "errorDisplayField": rule['Metadata']['errorDisplayField'],
                    "errorMessage": rule['Metadata']['errorMessage'],
                    "active": "true"
                }
            },
            "url":rule['attributes']['url'],
            "referenceId": rule['ValidationName'] + "_" + rule['EntityDefinition']['QualifiedApiName']
        }
    payload['compositeRequest'].append(body)

    if len(payload['compositeRequest']) == 25 or i == len(validationRules) - 1:
        payloads.append(payload.copy())
        payload['compositeRequest'] = []

#perform callouts
res = []
for i, load in enumerate(payloads):
    callback = sf.toolingexecute('composite/', data=load, method="POST")
    print("batch " + str(i+1) + " out of " + str(len(payloads)) + " completed")
    res.append(callback)

print("Job Completed!")

with open('result.json', 'w') as outfile: 
    outfile.write(json.dumps(res, indent=2))
