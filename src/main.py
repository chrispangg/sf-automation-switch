import os
from dotenv import load_dotenv
from controller import Controller

# Operation Toggles
disable_automation = False
enable_automation = False

# env variables
load_dotenv()
username = os.getenv("SFUSERNAME")
password = os.getenv("SFPASSWORD")
security_token = os.getenv("SECURITY_TOKEN")
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")
consumer_key = os.getenv("SF_CON_KEY")
consumer_secret = os.getenv("SF_CON_SECRET")

# init controller
controller = Controller(username, password, security_token, consumer_key, consumer_secret, org_alias, sfapi)
controller.initiate(disable_automation, enable_automation)
