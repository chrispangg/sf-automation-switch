import os
import subprocess
import shutil
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce

#Environment Variables
load_dotenv()
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")

#create empty org and fetch triggers
# subprocess.check_call("OrgInit.sh '%s'" % org_alias, shell=True)

#get names for Apex
with open('originalTriggerState.json', 'r') as json_file: 
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

#deploy source to org using the package.xml
deploy = subprocess.check_output("DeployToOrg.sh '%s'" % org_alias, shell=True)
print("script completed")


