from model import MetadataType
import json

class PayloadBuilder:
    def __init__(self):
        pass

    def composite_payloads(self, metadata_arr, metadata_type, turning_off):
        payloads = []  # 25 records per payload
        payload = {"allOrNone": False, "compositeRequest": []}
        for i, obj in enumerate(metadata_arr):
            body = self.payload_body_builder(metadata_type, obj, turning_off)
            payload["compositeRequest"].append(body)

            if len(payload["compositeRequest"]) == 25 or i == len(metadata_arr) - 1:
                payloads.append(payload.copy())
                payload["compositeRequest"] = []

        return payloads

    def payload_body_builder(self, metadata_type, model_obj, turning_off):
        body = {}
        if metadata_type == MetadataType.FLOW and turning_off == True:
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": {"activeVersionNumber": 0},
                },
                "url": model_obj.url,
                "referenceId": model_obj.name,
            }
        elif metadata_type == MetadataType.FLOW and turning_off == False:
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": {"activeVersionNumber": model_obj.active_version_num},
                },
                "url": model_obj.url,
                "referenceId": model_obj.name,
            }
        elif metadata_type == MetadataType.VALIDATIONRULE and turning_off == True:
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": {
                        "description": model_obj.description,
                        "errorConditionFormula": model_obj.errorConditionFormula,
                        "errorDisplayField": model_obj.errorDisplayField,
                        "errorMessage": model_obj.errorMessage,
                        "active": "false",
                    }
                },
                "url": model_obj.url,
                "referenceId": model_obj.name + "_" + model_obj.object,
            }
        elif metadata_type == MetadataType.VALIDATIONRULE and turning_off == False:
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": {
                        "description": model_obj.description,
                        "errorConditionFormula": model_obj.errorConditionFormula,
                        "errorDisplayField": model_obj.errorDisplayField,
                        "errorMessage": model_obj.errorMessage,
                        "active": model_obj.active,
                    }
                },
                "url": model_obj.url,
                "referenceId": model_obj.name + "_" + model_obj.object,
            }
        elif metadata_type == MetadataType.WORKFLOWRULE and turning_off == True:
            model_obj.metadata['active'] = False
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": model_obj.metadata
                },
                "url": model_obj.url,
                "referenceId": model_obj.id,
            }
        elif metadata_type == MetadataType.WORKFLOWRULE and turning_off == False:
            body = {
                "method": "PATCH",
                "body": {
                    "Metadata": eval(model_obj.metadata)
                },
                "url": model_obj.url,
                "referenceId": model_obj.id,
            }

        return body
