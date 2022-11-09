# sf-automation-switch

This script helps with disabling and enabling automation (Triggers, Flows, Process Builders, Workflow Rules, Duplicate Rules and Validation Rules) in a Salesforce org, especially useful for data migrations.

## ****How to Install and run the script****
- make sure the Salesforce CLI is installed
- Optional(recommended) - use a Python Virtual Environment i.e. venv, conda or virtualenv
    - If you are using venv, then locate the venv folder and activate i.e. source venv/bin/activate
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
        SFORGALIAS=TestOrg1
        SALESFORCE_API_VERSION=55.0
        ```
### How to Run:
The main.py is the main driver for all the logics. In it, the `disable_automation` and `enable_automation` booleans are used to trigger different set of logics. If `disable_automation` is true, it will attempt to disable Triggers, Validation Rules, Duplicate Rules, Flows, Process Builders and Workflow Rules in your org, while saving the original states. Similarly, toggling `enable_automation` to `True` will return the org back to it's original state. Nothing happens if both are set to `False`.

To run script, on the command line run: `python src/main.py`

### Sequence of operations:
#### Deactivating Automations
1. Setup an org project
2. Fetch Triggers Metadata from Org using the metadata api
3. Save the original state to a JSON file (OriginalTriggerState.json)
4. Change the Triggers state from 'Active' to 'Inactive'
5. Fetch Duplicate Rules Metadata from Org using the metadata api
6. Save the original state to a JSON file (OriginalDuplicateRuleState.json)
7. Change the Duplicate Rule state from 'Active' to 'Inactive'
8. Generate a package.xml for deploying Triggers and Duplicate Rules
9. Fetch FlowDefinitions Metadata from Org using the tooling api
10. Save the original state to a JSON file (OriginalFlowState.json)
11. Fetch Validation Rules Metadata from Org using the tooling api
12. Save the original state to a JSON file (OriginalValidationRuleState.json)
13. Fetch Workflow Rules Metadata from Org using the tooling api
14. Save the original state to a JSON file (OriginalWorkflowRuleState.json)
15. Create payloads for turning off FlowDefinitons, Validation Rules and Workflow Rules
16. Deploy Triggers via the metadata api, and FlowDefinitons, Validation Rules and Workflow Rules via the tooling api

#### Activating Automations
1. Reverse the changes using the original state using the json files generated in the deactivation process.
2. Clean-up project (delete "/output" folder)
