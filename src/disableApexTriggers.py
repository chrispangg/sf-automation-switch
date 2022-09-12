import os
import subprocess
import fileinput
import sys
import shutil
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

#get names of active triggers
# result = sf.toolingexecute('query/?q=SELECT+Id,NamespacePrefix,Name,Status,TableEnumOrId+From+ApexTrigger+WHERE+NamespacePrefix=+null+and+Status="Active"+Order+by+Name')
# jsonify = json.dumps(result, indent=2)
# with open('originalTriggerState.json', 'w') as outfile: 
#     outfile.write(jsonify)

#create empty org and fetch triggers
subprocess.check_call("OrgInit.sh '%s'" % org_alias, shell=True)

#get names for Apex
with open('output/sf-automation-switch-org/output.json') as json_file:
    data = json.load(json_file)
    result = data['result']['response']['fileProperties']
    
for trigger in result:
    #edge case: skip last line
    if trigger['fullName'] == "unpackaged/package.xml": continue

    #make a copy of the original trigger-meta.xml files    
    original_trigger_xml_path = 'output/sf-automation-switch-org/force-app/main/default/triggers/' + trigger['fullName'] + '.trigger-meta.xml'
    copied_trigger_xml_path = 'output/copiedTriggers/' + trigger['fullName'] + '.trigger-meta.xml'
    trigger_xml = open(copied_trigger_xml_path, 'w')
    shutil.copyfile(original_trigger_xml_path, copied_trigger_xml_path)

    # modify the meta.xml status to 'Inactive'
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

#deploy source to org using the package.xml
deploy = subprocess.check_output("DeployToOrg.sh '%s'" % org_alias, shell=True)
print(deploy)


