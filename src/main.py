import os
import subprocess
import fileinput
import sys
import math
import shutil
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce

#Operation Toggles
disableAutomation = False
enableAutomation = True

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

if disableAutomation:
    """Disable Apex Triggers"""
    #get names of active triggers and save them to a json file
    result = sf.toolingexecute('query/?q=SELECT+Id,NamespacePrefix,Name,Status,TableEnumOrId+From+ApexTrigger+WHERE+NamespacePrefix=+null+and+Status=\'Active\'+Order+by+Name')
    # result = sf.toolingexecute('query/?q=SELECT+Id,NamespacePrefix,Name,Status,TableEnumOrId+From+ApexTrigger+WHERE+NamespacePrefix=+null+Order+by+Name')
    jsonify = json.dumps(result, indent=2)
    with open('OriginalTriggerState.json', 'w') as outfile: 
        outfile.write(jsonify)

    #fetch triggers
    fetch = subprocess.check_call("FetchMetadata.sh {alias} {md_flag} {metadata}".format(alias=org_alias, md_flag="m", metadata='ApexTrigger'), stderr=subprocess.PIPE, text=True, shell=True)

    for trigger in result['records']:

        #make a copy of the original trigger-meta.xml files    
        original_trigger_xml_path = 'output/sf-automation-switch-org/force-app/main/default/triggers/' + trigger['Name'] + '.trigger-meta.xml'
        copied_trigger_xml_path = 'output/copiedTriggers/' + trigger['Name'] + '.trigger-meta.xml'
        shutil.copyfile(original_trigger_xml_path, copied_trigger_xml_path)

        #modify the meta.xml status to 'Inactive'
        for line in fileinput.FileInput(original_trigger_xml_path, inplace=1):
            line = line.replace("    <status>Active</status>", "    <status>Inactive</status>")
            sys.stdout.write(line)

    #generate package.xml
    package_xml = open('output/sf-automation-switch-org/manifest/package.xml','w+')
    package_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    package_xml.write('<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n')
    package_xml.write('    <types>\n        <members>*</members>\n        <name>ApexTrigger</name>\n    </types>\n')
    package_xml.write('    <version>' + str(sfapi) + '</version>\n')
    package_xml.write('</Package>')
    package_xml.close()

    """Disable Flows"""
    result = sf.toolingexecute('query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition+Where+ActiveVersion.VersionNumber!=null')
    # result = sf.toolingexecute('query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition')

    jsonify = json.dumps(result, indent=2)
    with open('OriginalFlowState.json', 'w') as outfile: 
        outfile.write(jsonify)

    print("Total flows: " + str(len(result['records'])) + " Total Batches: " + str(math.ceil(len(result['records'])/25)))
    
    # Create payloads
    payloads = [] #25 records per payload
    payload = {
        "allOrNone":False,
        "compositeRequest": []
    }

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
            payloads.append(payload.copy())
            payload['compositeRequest'] = []

    """Disable Validation Rules"""
    # get names of active validation rules and save them to a json file
    result = sf.toolingexecute('query/?q=SELECT+Id,Active,NamespacePrefix,ValidationName,EntityDefinitionId, EntityDefinition.QualifiedApiName +from+ValidationRule+WHERE+NamespacePrefix=null+and+Active=True')
    # result = sf.toolingexecute('query/?q=SELECT+Id,Active,NamespacePrefix,ValidationName,EntityDefinitionId,EntityDefinition.QualifiedApiName +from+ValidationRule+WHERE+NamespacePrefix=null')

    #get metadata of the validation rules
    validationRules = []
    print("fetching metadata for validation rule...")
    for rule in result['records']:
        result = sf.toolingexecute('query/?q=SELECT+Id,NamespacePrefix,ValidationName,EntityDefinition.QualifiedApiName,Metadata+from+ValidationRule+WHERE+NamespacePrefix=null+and+Id=\'{id}\''.format(id=rule['Id']))
        validationRules.append(result['records'][0])
    
    jsonify = json.dumps(validationRules, indent=2)
    with open('OriginalValidationRuleState.json', 'w') as outfile:
        outfile.write(jsonify)

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
        
    """Deployment Begins"""
    print("Deployment starts...")
    print("Deploying Triggers")
    #deploy source to org using the package.xml for triggers
    deploy = subprocess.check_output("DeployToOrg.sh '%s'" % org_alias, shell=True, stderr=subprocess.PIPE, text=True)
    print("deployed Triggers")

    #perform callouts for validation rules and flows
    print("Deploying Flows and Validation Rules")
    res = []
    for i, load in enumerate(payloads):
        callback = sf.toolingexecute('composite/', data=load, method="POST")
        print("batch " + str(i+1) + " out of " + str(len(payloads)) + " completed")
        res.append(callback)
    print("deployed Flows and Validation Rules")
    print("Job completed for deactivating automation. Check result in result.json")

    with open('result.json', 'w') as outfile: 
        outfile.write(json.dumps(res, indent=2))
    
if enableAutomation:
    """Enable Triggers"""
    #get names for Apex
    with open('OriginalTriggerState.json', 'r') as json_file: 
        result = json.load(json_file)
        
    for trigger in result['records']:
        #replace triggers with the originals
        original_trigger_xml_path = 'output/sf-automation-switch-org/force-app/main/default/triggers/' + trigger['Name'] + '.trigger-meta.xml'
        copied_trigger_xml_path = 'output/copiedTriggers/' + trigger['Name'] + '.trigger-meta.xml'
        shutil.move(copied_trigger_xml_path, original_trigger_xml_path)

    #generate package.xml
    package_xml = open('output/sf-automation-switch-org/manifest/package.xml','w+')
    package_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    package_xml.write('<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n')
    package_xml.write('    <types>\n        <members>*</members>\n        <name>ApexTrigger</name>\n    </types>\n')
    package_xml.write('    <version>' + str(sfapi) + '</version>\n')
    package_xml.write('</Package>')
    package_xml.close()

    """Enable Flows"""
    #get Flow state to return from OriginalFlowState
    with open('OriginalFlowState.json') as outfile:
        data = json.load(outfile)

    print("Total flows: " + str(len(data['records'])) + " Total Batches: " + str(math.ceil(len(data['records'])/25)))

    payloads = [] #25 records per payload
    payload = {
        "allOrNone":False,
        "compositeRequest": []
    }

    for i, flow in enumerate(data['records']):
        body = {
            "method":"PATCH",
            "body":{
                "Metadata":{
                    "activeVersionNumber": flow["ActiveVersion"]["VersionNumber"]
                    # "activeVersionNumber": flow["LatestVersion"]["VersionNumber"]
                    },
                },
                "url": flow["attributes"]["url"],
                "referenceId": flow["DeveloperName"]
        }
        payload['compositeRequest'].append(body)

        if len(payload['compositeRequest']) == 25 or i == len(data['records']) - 1:
            payloads.append(payload.copy())
            payload['compositeRequest'] = []

    """Enable Validation Rules"""
    with open('OriginalValidationRuleState.json', 'r') as readfile:
        validationRules = json.load(readfile)

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

    """Deployment Begins"""
    print("Deployment starts...")
    print("Deploying Triggers")
    #deploy source to org using the package.xml
    deploy = subprocess.check_output("DeployToOrg.sh '%s'" % org_alias, shell=True)
    print("deployed Triggers")

    #perform callouts for validation rules and flows
    print("Deploying Flows and Validation Rules")
    res = []
    for i, load in enumerate(payloads):
        callback = sf.toolingexecute('composite/', data=load, method="POST")
        print("batch " + str(i+1) + " out of " + str(len(payloads)) + " completed")
        res.append(callback)

    print("deployed Flows and Validation Rules")
    print("Job completed for activating automation. Check result in result.json")

    with open('result.json', 'w') as outfile: 
        outfile.write(json.dumps(res, indent=2))
    