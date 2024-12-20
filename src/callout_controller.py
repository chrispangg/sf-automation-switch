from simple_salesforce import Salesforce
import json
import os
class CalloutController:
    def __init__(self, username, password, security_token, consumer_key, consumer_secret, org_alias):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            domain="test",
        )
        self.org_alias = org_alias

    def fetch_active_apex_triggers_json(self):
        return self.sf.toolingexecute(
            "query/?q=SELECT+Id,NamespacePrefix,Name,Status,TableEnumOrId+From+ApexTrigger+WHERE+NamespacePrefix=+null+and+Status='Active'+Order+by+Name"
        )

    def fetch_all_apex_triggers_json(self):
        return self.sf.toolingexecute(
            "query/?q=SELECT+Id,NamespacePrefix,Name,Status,TableEnumOrId+From+ApexTrigger+WHERE+NamespacePrefix=+null+Order+by+Name"
        )
    
    def fetch_all_active_duplicate_rules(self):
        return self.sf.query("Select Id, SobjectType, SobjectSubtype, DeveloperName, isActive FROM DuplicateRule where isActive = True")

    def fetch_all_flows_json(self):
        return self.sf.toolingexecute(
            "query/?q=Select+Id,ActiveVersion.VersionNumber,LatestVersion.VersionNumber,DeveloperName+From+FlowDefinition+Where+ActiveVersion.VersionNumber!=null"
        )

    def fetch_all_active_validation_rules_json(self):
        return self.sf.toolingexecute(
            "query/?q=SELECT+Id,Active,NamespacePrefix,ValidationName,EntityDefinitionId, EntityDefinition.QualifiedApiName +from+ValidationRule+WHERE+NamespacePrefix=null+and+Active=True"
        )

    def fetch_all_validation_rules_json(self):
        return self.sf.toolingexecute(
            "query/?q=SELECT+Id,Active,NamespacePrefix,ValidationName,EntityDefinitionId,EntityDefinition.QualifiedApiName+from+ValidationRule+WHERE+NamespacePrefix=null"
        )

    def fetch_single_validation_rule_with_metadata(self, record_id):
        return self.sf.toolingexecute(
            "query/?q=SELECT+Id,NamespacePrefix,ValidationName,EntityDefinition.QualifiedApiName,Metadata+from+ValidationRule+WHERE+NamespacePrefix=null+and+Id='{id}'".format(id=record_id))

    def fetch_all_workflow_rules_json(self):
        return self.sf.toolingexecute("query/?q=SELECT+Id,Name,TableEnumOrId+FROM+WorkflowRule")

    def fetch_single_workflow_rule_with_metadata(self, record_id):
        return self.sf.toolingexecute("query/?q=SELECT+Id,+Name,+Metadata+FROM+WorkflowRule+WHERE+Id='{id}'".format(id=record_id))

    def tooling_composite(self, payload):
        return self.sf.toolingexecute("composite/", data=payload, method="POST")

    def tooling_composite_multiple(self, payloads):
        res = []
        for i, load in enumerate(payloads):
            callback = self.sf.toolingexecute("composite/", data=load, method="POST")
            print(
                "batch " + str(i + 1) + " out of " + str(len(payloads)) + " completed"
            )
            res.append(callback)
        return res

    def deploy_payloads(self, payloads):
        # perform callouts for validation rules and flows
        
        res = []
        for i, load in enumerate(payloads):
            callback = self.sf.toolingexecute("composite/", data=load, method="POST")
            print("batch " + str(i + 1) + " out of " + str(len(payloads)) + " completed")
            res.append(callback)

        with open("result.json", "w") as outfile:
            outfile.write(json.dumps(res, indent=2))