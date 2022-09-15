from enum import Enum
import json


class MetadataType(Enum):
    TRIGGER = "ApexTrigger"
    FLOW = "Flows"
    VALIDATIONRULE = "ValidationRule"


class Metadata:
    id: str
    name: str
    url: str

    def __init__(self, id, name, url) -> None:
        self.id = id
        self.name = name
        self.url = url

    def __str__(self):
        return "id: {}, name: {}, url:{}".format(self.id, self.name, self.url)


class Trigger(Metadata):
    status: str
    object: str
    type: MetadataType

    def __init__(self, id, name, url, status, object, type=MetadataType.TRIGGER):
        super().__init__(id, name, url)
        self.status = status
        self.object = object
        self.type = type

    def __str__(self):
        return "id: {}, name: {}, status: {}, object: {}".format(
            self.id, self.name, self.status, self.object
        )


class FlowDefinition(Metadata):
    active_version_num: int
    type: MetadataType

    def __init__(self, id, name, url, active_version_num, type=MetadataType.FLOW):
        super().__init__(id, name, url)
        self.active_version_num = active_version_num
        self.type = type

    def __str__(self):
        return "id: {}, name: {}, active_version_num: {}".format(
            self.id, self.name, self.active_version_num
        )


class ValidationRule(Metadata):
    description: str
    errorConditionFormula: str
    errorDisplayField: str
    errorMessage: str
    active: bool
    object: str
    type: MetadataType

    def __init__(
        self,
        id,
        name,
        url,
        description,
        errorConditionFormula,
        errorDisplayField,
        errorMessage,
        active,
        object,
        type=MetadataType.VALIDATIONRULE,
    ):
        super().__init__(id, name, url)
        self.description = description
        self.errorConditionFormula = errorConditionFormula
        self.errorDisplayField = errorDisplayField
        self.errorMessage = errorMessage
        self.active = active
        self.object = object
        self.type = type

    def __str__(self):
        return "id: {}, name: {}, description: {}, active: {}".format(
            self.id, self.name, self.description, self.active
        )
