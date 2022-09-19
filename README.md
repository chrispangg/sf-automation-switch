# sf-automation-switch

This script helps with disabling and enabling automation (Triggers, Validation Rules and Flows) in a Salesforce org, especially useful for data migrations.

## ****How to Install and run the script****
- make sure the Salesforce CLI is installed
- Optional - use a Python Virtual Environment i.e. venv, conda or virtualenv
- Make sure the packages are installed in your local machine by running :`pip install -r requirements.txt`
- Setup `.env` file at the root level. 
    - SFUSERNAME - username for logging into the Salesforce Org
    - SFPASSWORD - password for your SFUSERNAME
    - SECURITY_TOKEN -  usually provided when you change your password. Or get a new one from Personal Settings > Reset My Security Token
    - SFORGALIAS - sfdx alias for your Salesforce Org in your local machine
        - Can use the following command to set it up: `sfdx auth:web:login -a TestOrg1 -r https://MyDomainName--SandboxName.sandbox.my.salesforce.com`, where `TestOrg1` is your SFORGALIAS.
    - Example:
        ```bash
        SFUSERNAME=user@email.com.dev
        SFPASSWORD=00000000000
        SECURITY_TOKEN=0000000000000000000000000
        SFORGALIAS= TestOrg1
        SALESFORCE_API_VERSION=XX.0
        ```
### How to Run:
The main.py is the main driver for all the logics. In it, the `disable_automation` and `enable_automation` booleans are used to trigger different set of logics. If `disable_automation` is true, it will attempt to disable Triggers, Validation Rules and Flows in your org. Similarly, toggling `enable_automation`  to `True` will enable Triggers, Validation Rules and Flows in your org. Nothing happen if both are set to `False`.

To run script, on the command line run: `python src/main.py`
