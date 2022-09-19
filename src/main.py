import os
import subprocess
import fileinput
import sys
import math
import shutil
from dotenv import load_dotenv
import json
from model import MetadataType
from callout_controller import CalloutController
from json_util import JsonUtil
from xml_util import XmlUtil
from payload_builder import PayloadBuilder
from model import MetadataType
from schema import TriggerSchema, FlowDefinitionSchema, ValidationRuleSchema
from clean_up import CleanUpUtil

# Operation Toggles
disable_automation = False
enable_automation = True

if not disable_automation and not enable_automation:
    print("No operations are toggled")
    sys.exit()

# env variables
load_dotenv()
username = os.getenv("SFUSERNAME")
password = os.getenv("SFPASSWORD")
security_token = os.getenv("SECURITY_TOKEN")
org_alias = os.getenv("SFORGALIAS")
sfapi = os.getenv("SALESFORCE_API_VERSION")

# authenticate
sf = CalloutController(username, password, security_token, org_alias)

# Setup Shell Org if not exists
if not os.path.exists("output/sf-automation-switch-org"):
    orgInit = subprocess.check_call(
        "scripts\OrgInit.sh '%s'" % org_alias, stderr=subprocess.PIPE, text=True, shell=True
    )
else:
    print("org already exist, no org setup required")

if disable_automation:
    """Disable Apex Triggers"""
    # get names of active triggers and save them as object and export as json file
    result = sf.fetch_active_apex_triggers_json()
    json_helper = JsonUtil()
    trigger_arr = json_helper.json_to_trigger_objects(result)
    trigger_schema_arr = TriggerSchema().dump(trigger_arr, many=True)
    json_helper.array_to_json("output/json/OriginalTriggerState.json", trigger_schema_arr)

    # fetch triggers in source files
    fetch = subprocess.check_call(
        "scripts\FetchMetadata.sh {alias} {md_flag} {metadata}".format(
            alias=org_alias, md_flag="m", metadata="ApexTrigger"
        ),
        stderr=subprocess.PIPE,
        text=True,
        shell=True,
    )

    for trigger in trigger_arr:
        # make a copy of the original trigger-meta.xml files
        original_trigger_xml_path = (
            "output/sf-automation-switch-org/force-app/main/default/triggers/"
            + trigger.name
            + ".trigger-meta.xml"
        )
        copied_trigger_xml_path = (
            "output/copiedTriggers/" + trigger.name + ".trigger-meta.xml"
        )
        shutil.copyfile(original_trigger_xml_path, copied_trigger_xml_path)

        # modify the meta.xml status to 'Inactive'
        for line in fileinput.FileInput(original_trigger_xml_path, inplace=1):
            line = line.replace(
                "    <status>Active</status>", "    <status>Inactive</status>"
            )
            sys.stdout.write(line)

    # generate package.xml
    write_apex_package = XmlUtil.generate_trigger_package(
        "output/sf-automation-switch-org/manifest/package.xml", sfapi
    )

    """Disable Flows"""
    result = sf.fetch_all_flows_json()
    flow_definition_arr = json_helper.json_to_flow_objects(result)
    flow_definition_schema_arr = FlowDefinitionSchema().dump(
        flow_definition_arr, many=True
    )
    json_helper.array_to_json("output/json/OriginalFlowState.json", flow_definition_schema_arr)

    print(
        "Total flows: "
        + str(len(flow_definition_arr))
        + " Total Batches: "
        + str(math.ceil(len(flow_definition_arr) / 25))
    )

    # Create payloads
    payload_builder = PayloadBuilder()
    flow_payloads = payload_builder.composite_payloads(
        flow_definition_arr, MetadataType.FLOW, True
    )

    """Disable Validation Rules"""
    # get active validation rules and save them to a json file
    result = sf.fetch_all_active_validation_rules_json()
    print("fetching metadata for validation rule...")
    validation_rule_arr = json_helper.json_to_validation_rule_objects(result, sf)
    validation_rule_schema_arr = ValidationRuleSchema().dump(
        validation_rule_arr, many=True
    )
    json_helper.array_to_json(
        "output/json/OriginalValidationRuleState.json", validation_rule_schema_arr
    )

    #create payload
    payloads_validation_rules = payload_builder.composite_payloads(
        validation_rule_arr, MetadataType.VALIDATIONRULE, True
    )

    print("Deployment starts...")
    print("Deploying Triggers")
    # deploy source to org using the package.xml for triggers
    subprocess.check_output("scripts\DeployToOrg.sh '%s'" % org_alias, shell=True)
    print("Deployed Triggers")
    # deploy payloads
    payloads = flow_payloads + payloads_validation_rules
    print("Deploying Flows and Validation Rules")
    sf.deploy_payloads(payloads)
    print("Deployed Flows and Validation Rules")
    print("Job completed for activating automation. Check result in result.json")

if enable_automation:
    """Enable Triggers"""
    # get names for Apex
    trigger_arr = []
    with open("output/json/OriginalTriggerState.json", "r") as json_file:
        trigger_json = json.load(json_file)
        for t in trigger_json:
            result = TriggerSchema().load(t)
            trigger_arr.append(result)
    
    for trigger in trigger_arr:
        # replace triggers with the originals
        original_trigger_xml_path = (
            "output/sf-automation-switch-org/force-app/main/default/triggers/"
            + trigger.name
            + ".trigger-meta.xml"
        )
        copied_trigger_xml_path = (
            "output/copiedTriggers/" + trigger.name + ".trigger-meta.xml"
        )
        shutil.move(copied_trigger_xml_path, original_trigger_xml_path)

    # generate package.xml
    write_apex_package = XmlUtil.generate_trigger_package(
        "output/sf-automation-switch-org/manifest/package.xml", sfapi
    )

    """Enable Flows"""
    # get Flow state to return from OriginalFlowState
    flow_definition_arr = []
    with open("output/json/OriginalFlowState.json") as outfile:
        flow_definition_json = json.load(outfile)
        for f in flow_definition_json:
            result = FlowDefinitionSchema().load(f)
            flow_definition_arr.append(result)

    print(
        "Total flows: "
        + str(len(flow_definition_arr))
        + " Total Batches: "
        + str(math.ceil(len(flow_definition_arr) / 25))
    )

    payload_builder = PayloadBuilder()
    flow_payloads = payload_builder.composite_payloads(
        flow_definition_arr, MetadataType.FLOW, False
    )

    """Enable Validation Rules"""
    validation_rule_arr = []
    with open("output/json/OriginalValidationRuleState.json", "r") as readfile:
        validation_rule_json = json.load(readfile)
        for v in validation_rule_json:
            result = ValidationRuleSchema().load(v)
            validation_rule_arr.append(result)

    #create payload
    payloads_validation_rules = payload_builder.composite_payloads(
        validation_rule_arr, MetadataType.VALIDATIONRULE, False
    )
    
    
    print("Deployment starts...")
    print("Deploying Triggers")
    # deploy source to org using the package.xml for triggers
    subprocess.check_output("scripts\DeployToOrg.sh '%s'" % org_alias, shell=True)
    print("Deployed Triggers")
    # deploy payloads
    payloads = flow_payloads + payloads_validation_rules
    print("Deploying Flows and Validation Rules")
    sf.deploy_payloads(payloads)
    print("Deployed Flows and Validation Rules")
    print("Job completed for deactivating automation. Check result in result.json")
    
    print("Cleanup begins...")
    delete = CleanUpUtil().delete("output")
    delete = CleanUpUtil().delete("result.json")
    print("Cleanup completed")