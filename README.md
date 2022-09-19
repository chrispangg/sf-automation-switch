# sf-automation-switch

This script helps with disabling and enabling automation (Triggers, Validation Rules and Flows) in a Salesforce org, especially useful for data migrations.

## ****How to Install and run the script****

- Make sure you have the packages installed in your local machine by running :
    `pip install -r requirements.txt`
- Setup `.env` file at the root level. Example:
    
    ```bash
    SFUSERNAME=user@email.com.dev
    SFPASSWORD=00000000000
    SECURITY_TOKEN=0000000000000000000000000
    SFORGALIAS= abc_sfdev
    SALESFORCE_API_VERSION=XX.0
    ```
    
### How to Run:

The `disable_automation` and `enable_automation` booleans trigger the logic in the script. If `disable_automation` is true, it will attempt to disable Triggers, Validation Rules and Flows in your org. Similarly, toggling `enable_automation`  to `True` will enable Triggers, Validation Rules and Flows in your org. Nothing happen if both are set to `False`.
