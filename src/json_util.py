import json
from model import Trigger, FlowDefinition, ValidationRule, DuplicateRule, WorkflowRule

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__

class JsonUtil:
    def __init__(self):
        pass

    def json_to_trigger_objects(self, json):
        triggers = []
        for item in json["records"]:
            trigger = Trigger(
                id=item["Id"], 
                name=item["Name"], 
                url=item["attributes"]["url"],
                status=item['Status'],
                object=item["TableEnumOrId"]
            )
            triggers.append(trigger)
        return triggers

    def json_to_duplicate_rule_objects(self, json):
        duplicate_rules = []
        for item in json["records"]:
            objectType = item["SobjectSubtype"] if item["SobjectSubtype"] != "None" else item["SobjectType"]
            duplicate_rule = DuplicateRule(
                id=item["Id"],
                name=item["DeveloperName"],
                url=item["attributes"]["url"],
                isActive=item["IsActive"],
                object=objectType
            )
            duplicate_rules.append(duplicate_rule)
        return duplicate_rules

    def json_to_flow_objects(self, json):
        flow_definitions = []
        for item in json["records"]:
            flow_definition = FlowDefinition(
                item["Id"],
                item["DeveloperName"],
                item["attributes"]["url"],
                item["ActiveVersion"]["VersionNumber"],
            )
            flow_definitions.append(flow_definition)
        return flow_definitions

    def json_to_workflow_rule_objects(self, json, sf):
        workflow_rules = []
        for rule in json["records"]:
            #Skip Question related workflow rules as they causes SOQL issues
            if rule["TableEnumOrId"] == "Question": continue 
            fetch_res = sf.fetch_single_workflow_rule_with_metadata(rule["Id"])
            item = fetch_res['records'][0] 
            workflow = WorkflowRule(
                id=item["Id"],
                name=item["Name"],
                url=item["attributes"]["url"],
                active=item["Metadata"]["active"],
                metadata=item["Metadata"],
            )
            workflow_rules.append(workflow)
        return workflow_rules

    def json_to_validation_rule_objects(self, json, sf):
        validation_rules = []
        for rule in json["records"]:
            fetch_res = sf.fetch_single_validation_rule_with_metadata(rule["Id"])
            item = fetch_res['records'][0]
            validation_rule = ValidationRule(
                id=item["Id"],
                name=item["ValidationName"],
                url=item["attributes"]["url"],
                description=item["Metadata"]["description"],
                errorConditionFormula=item["Metadata"]["errorConditionFormula"],
                errorDisplayField=item["Metadata"]["errorDisplayField"],
                errorMessage=item["Metadata"]["errorMessage"],
                active=item["Metadata"]["active"],
                object=item["EntityDefinition"]["QualifiedApiName"],
            )
            validation_rules.append(validation_rule)
        return validation_rules
    
    def array_to_json(self, name, arr):
        with open("{name}".format(name=name), "w") as outfile:
            jsonify = json.dumps(arr, indent=2)
            outfile.write(jsonify)

