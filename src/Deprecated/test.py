from simple_salesforce import Salesforce
import json
import os
from dotenv import load_dotenv
#Environment Variables
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

result = sf.toolingexecute('query/?q=Select Id,Name, Metadata From WorkflowRule limit 1')
jsonify = json.dumps(result, indent=2)
print(jsonify)