import os
from dotenv import load_dotenv
import json
from simple_salesforce import Salesforce
import math
import 

#login details
load_dotenv()
username = os.getenv('SFUSERNAME')
password = os.getenv('SFPASSWORD')
security_token = os.getenv('SECURITY_TOKEN')

#authenticate
sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

#Get flows 
flowStates = sf.toolingexecute('query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition+Where+ActiveVersion.VersionNumber!=null')

#Operation Toggles
disableFlows = False

enableFlows = False


