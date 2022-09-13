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
result = sf.toolingexecute('query/?q=SELECT+Id,Active,NamespacePrefix,ValidationName,EntityDefinitionId, EntityDefinition.QualifiedApiName +from+ValidationRule+WHERE+NamespacePrefix=null+and+Active=True')

#get metadata of the validation rules
validationRules = []
for rule in result['records']:
    print("fetching metadata for validation rule: " + rule['ValidationName'])

    result = sf.toolingexecute('query/?q=SELECT+Id,NamespacePrefix,ValidationName,EntityDefinition.QualifiedApiName,Metadata+from+ValidationRule+WHERE+NamespacePrefix=null+and+Active=True+and+Id=\'{id}\''.format(id=rule['Id']))

    validationRules.append(result['records'][0])

jsonify = json.dumps(validationRules, indent=2)
with open('ValidationRulesWithMetadata.json', 'w') as outfile:
    outfile.write(jsonify)

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
                    "active": "false"
                }
            },
            "url":rule['attributes']['url'],
            "referenceId": rule['ValidationName'] + "_" + rule['EntityDefinition']['QualifiedApiName']
        }
    payload['compositeRequest'].append(body)

    if len(payload['compositeRequest']) == 25 or i == len(result['records']) - 1:
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

# #testing
# payload = {
#     "allOrNone":False,
#     "compositeRequest": []
# }
# body = {
#     "method":"PATCH",
#     "body":{
#         "Metadata": {
#             "description": "Validates if Reason for Date Change has been entered when changing Category.",
#             "errorConditionFormula": "AND(\n(RecordType.DeveloperName = 'Service_Company_Work_Order' ||\nRecordType.DeveloperName = 'Service_Company_Resolution_Plan'\n),\nISCHANGED(Category__c),\nISBLANK(TEXT( Reason_for_Date_Change__c ))\n)",
#             "errorDisplayField": "Reason_for_Date_Change__c",
#             "errorMessage": "Reason for Date Change cannot be blank if Category is changed. Please enter the reason for date change.",
#             "active": "true"
#             }
#         },
#         "url":"/services/data/v52.0/tooling/sobjects/ValidationRule/03d2O000000JaiwQAC",
#         "referenceId": "Fire_the_Rule_If_Category_Changes"
#     }








# #build package.xml for validation rules retrieval
# package_xml = open('output/sf-automation-switch-org/manifest/package.xml','w+')
# package_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
# package_xml.write('<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n')
# package_xml.write('    <types>\n')
# for rule in result['records']:
#     package_xml.write('        <members>{object}.{ruleName}</members>\n'.format(
#         object=rule['EntityDefinition']['QualifiedApiName'], 
#         ruleName=rule['ValidationName']))

# package_xml.write('        <name>ValidationRule</name>\n    </types>\n')
# package_xml.write('    <version>' + str(sfapi) + '</version>\n')
# package_xml.write('</Package>')
# package_xml.close()

# #fetch all validations from the package.xml
# fetch = subprocess.check_call("FetchMetadata.sh {alias} {md_flag} {metadata}".format(alias=org_alias, md_flag="x", metadata='manifest/package.xml'), stderr=subprocess.PIPE, text=True, shell=True)




# print(orgInit.stderr)
# for trigger in result['records']:

#     #make a copy of the original trigger-meta.xml files    
#     original_trigger_xml_path = 'output/sf-automation-switch-org/force-app/main/default/triggers/' + trigger['fullName'] + '.trigger-meta.xml'
#     copied_trigger_xml_path = 'output/copiedTriggers/' + trigger['fullName'] + '.trigger-meta.xml'
#     shutil.copyfile(original_trigger_xml_path, copied_trigger_xml_path)

#     #modify the meta.xml status to 'Inactive'
#     for line in fileinput.FileInput(original_trigger_xml_path, inplace=1):
#         line = line.replace("    <status>Active</status>", "    <status>Inactive</status>")
#         sys.stdout.write(line)
