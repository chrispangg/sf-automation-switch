from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField
from model import MetadataType, Trigger, ValidationRule, FlowDefinition, DuplicateRule, WorkflowRule

class TriggerSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    status = fields.Str()
    object = fields.Str()
    type = EnumField(MetadataType)

    @post_load
    def make_trigger(self, data, **kwargs):
        return Trigger(**data)

class DuplicateRuleSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    isActive = fields.Bool()
    type = EnumField(MetadataType)
    object = fields.Str()

    @post_load
    def make_duplicate_rule(self, data, **kwargs):
        return DuplicateRule(**data)

class FlowDefinitionSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    active_version_num = fields.Int()
    type = EnumField(MetadataType)

    @post_load
    def make_flow_definition(self, data, **kwargs):
        return FlowDefinition(**data)

class WorkflowRuleSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    active = fields.Bool()
    type = EnumField(MetadataType)
    metadata = fields.Str()

    @post_load
    def make_workflow_rule(self, data, **kwargs):
        return WorkflowRule(**data)

class ValidationRuleSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    url = fields.Str()
    description = fields.Str(allow_none=True)
    errorConditionFormula = fields.Str()
    errorDisplayField = fields.Str(allow_none=True)
    errorMessage = fields.Str()
    active = fields.Bool()
    object= fields.Str()
    type = EnumField(MetadataType)

    @post_load
    def make_validation_rule(self, data, **kwargs):
        return ValidationRule(**data)