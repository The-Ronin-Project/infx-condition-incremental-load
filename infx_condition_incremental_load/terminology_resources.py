import requests
import json
import dataclasses
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from decouple import config
from infx_condition_incremental_load.core_data_types import *

BASE_URL = config("INTERNAL_TOOLS_API_BASE_URL")

@dataclass
class Concept:
    code: str
    display: str
    system: Optional[str] = None
    version: Optional[str] = None


class Terminology:
    def __init__(
            self,
            uuid,
            name: str,
            version: str,
            effective_start,
            effective_end,
            fhir_uri: str,
    ):
        self.uuid = uuid
        self.name = name
        self.version = version
        self.effective_start = effective_start
        self.effective_end = effective_end
        self.fhir_uri = fhir_uri
        self.codes = []

    def __eq__(self, other):
        if not isinstance(other, Terminology):
            return NotImplemented
        return ((self.fhir_uri, self.version) == (other.fhir_uri, other.version) or
                (self.name, self.version) == (other.name, other.version)) and \
               (self.uuid == other.uuid or (self.uuid is None and other.uuid is None))

    def __hash__(self):
        return hash((self.fhir_uri, self.version, self.name))

    def __repr__(self):
        return f"Terminology(uuid={self.uuid}, name={self.name}, version={self.version}, effective_start={self.effective_start}, effective_end={self.effective_end}, fhir_uri={self.fhir_uri})"

    def load_additional_concepts(self, concepts: List[Concept]):
        url = f"{BASE_URL}/terminology/new_code"
        headers = {'Content-Type': 'application/json'}

        # Convert concepts to list of dictionaries
        concepts_dict = [dataclasses.asdict(concept) for concept in concepts]

        for concept_dict in concepts_dict:
            concept_dict['terminology_version_uuid'] = self.uuid
            response = requests.post(url, headers=headers, data=json.dumps(concept_dict))
            response.raise_for_status()  # ensure we notice bad responses

            # Now that the concept is loaded, we can add it to the local list
            self.codes.append(Concept(**concept_dict))


@dataclass
class Expansion:
    timestamp: str
    contains: List[Concept] = field(default_factory=list)


class ValueSet:
    def __init__(self, uuid):
        self.uuid = uuid

    def lookup_versions(self) -> List['ValueSetVersion']:
        """
        Looks up all available versions of a value set and returns them in a list
        :return:
        """
        pass


class ValueSetVersion:
    def __init__(self, additional_data, contact, description, experimental, extension, id,
                 immutable, meta, name, publisher, purpose, resource_type, status, title, url, version, expansion):
        self.additional_data = additional_data
        self.contact = contact
        self.description = description
        self.experimental = experimental
        self.extension = extension
        self.id = id
        self.immutable = immutable
        self.meta = meta
        self.name = name
        self.publisher = publisher
        self.purpose = purpose
        self.resource_type = resource_type
        self.status = status
        self.title = title
        self.url = url
        self.version = version
        self.expansion = expansion

    @classmethod
    def load(cls, uuid):
        response = requests.get(f"{BASE_URL}/ValueSet/{uuid}/$expand")
        response.raise_for_status()  # ensure we notice bad responses
        json_object = response.json()
        expansion_data = json_object.get('expansion', {})
        expansion = Expansion(
            timestamp=expansion_data.get('timestamp', ""),
            contains=[Concept(**concept) for concept in expansion_data.get('contains', [])]
        )
        return cls(additional_data=json_object.get('additionalData', {}),
                   contact=json_object.get('contact', []),
                   description=json_object.get('description', ""),
                   experimental=json_object.get('experimental', False),
                   extension=json_object.get('extension', []),
                   id=json_object.get('id', ""),
                   immutable=json_object.get('immutable', False),
                   meta=json_object.get('meta', {}),
                   name=json_object.get('name', ""),
                   publisher=json_object.get('publisher', ""),
                   purpose=json_object.get('purpose', ""),
                   resource_type=json_object.get('resourceType', ""),
                   status=json_object.get('status', ""),
                   title=json_object.get('title', ""),
                   url=json_object.get('url', ""),
                   version=json_object.get('version', ""),
                   expansion=expansion)

    def new_version(self, description: str):
        url = f"{BASE_URL}/ValueSets/{self.id}/versions/new"

        # Prepare request data
        data = {
            'description': description
        }

        # Make the request
        response = requests.post(url, json=data)
        response.raise_for_status()  # ensure we notice bad responses

        # Return the response JSON, in case it's needed
        return response.json()

    def update_rules_for_new_terminology_version(self, old_terminology_version_uuid: str,
                                                 new_terminology_version_uuid: str):
        url = f"{BASE_URL}/ValueSets/_/versions/{self.id}/rules/update_terminology"

        # Prepare request data
        data = {
            'old_terminology_version_uuid': old_terminology_version_uuid,
            'new_terminology_version_uuid': new_terminology_version_uuid
        }

        # Make the request
        response = requests.post(url, json=data)
        response.raise_for_status()  # ensure we notice bad responses

        # Return the response JSON, in case it's needed
        return response.json()

    def publish(self):
        url = f"{BASE_URL}/ValueSets/{self.id}/published"

        # Make the request
        response = requests.post(url)
        response.raise_for_status()  # ensure we notice bad responses

        # Return the response JSON, in case it's needed
        return response.json()

    def lookup_terminologies_in_value_set_version(self) -> List['Terminology']:
        terminologies: Dict[Tuple[str, str], Terminology] = dict()

        for concept in self.expansion.contains:
            key = (concept.system, concept.version)
            if key not in terminologies:
                # For the sake of this implementation, we will use dummy values for
                # uuid, name, effective_start, effective_end, as these values are not available
                # in the Concept class. Ideally, these values should come from appropriate sources.
                terminologies[key] = Terminology(
                    uuid=None,
                    name=None,
                    version=concept.version,
                    effective_start=None,
                    effective_end=None,
                    fhir_uri=concept.system
                )

        return list(terminologies.values())


class ConceptMap:
    def __init__(self, uuid):
        self.uuid = uuid


class ConceptMapVersion:
    def __init__(self,
                 uuid,
                 source_value_set_version: ValueSetVersion,
                 target_value_set_version: ValueSetVersion):
        self.uuid = uuid
        self.source_value_set_version = source_value_set_version
        self.target_value_set_version = target_value_set_version

    @classmethod
    def load(cls, concept_map_version_uuid):
        # Make request to /ConceptMaps/:concept_map_version_uuid
        concept_map_request = requests.get(f"{BASE_URL}/ConceptMaps/{concept_map_version_uuid}")
        concept_map_request.raise_for_status()  # ensure we notice bad responses
        json_data = concept_map_request.json()

        return cls.deserialize(json_data)

    @classmethod
    def deserialize(cls, json):
        uuid = json.get('id')
        source_value_set_version_uuid = json.get('internalData').get('source_value_set_version_uuid')
        target_value_set_version_uuid = json.get('internalData').get('target_value_set_version_uuid')

        source_value_set_version = ValueSetVersion.load(source_value_set_version_uuid)
        target_value_set_version = ValueSetVersion.load(target_value_set_version_uuid)
        return cls(uuid=uuid,
                   source_value_set_version=source_value_set_version,
                   target_value_set_version=target_value_set_version)

    def new_version(self, previous_version_uuid: str, new_version_description: str, new_version_num: int,
                    new_source_value_set_version_uuid: str, new_target_value_set_version_uuid: str):
        url = f"{BASE_URL}/ConceptMaps/actions/new_version_from_previous"

        # Prepare request data
        data = {
            "previous_version_uuid": previous_version_uuid,
            "new_version_description": new_version_description,
            "new_version_num": new_version_num,
            "new_source_value_set_version_uuid": new_source_value_set_version_uuid,
            "new_target_value_set_version_uuid": new_target_value_set_version_uuid
        }

        # Make the request
        response = requests.post(url, json=data)
        response.raise_for_status()  # ensure we notice bad responses

        # Return the response JSON, in case it's needed
        return response.json()

    def publish(self):
        url = f"{BASE_URL}/ConceptMaps/{self.uuid}/published"

        # Make the request
        response = requests.post(url)
        response.raise_for_status()  # ensure we notice bad responses

        # Return the response JSON, in case it's needed
        return response.json()


# todo: Identify relevant terminology, value set, and concept map
# Lookup based on: organization_id, data type
def lookup_concept_map_version_for_resource_type(resource_type: ResourceType,
                                                 organization: Organization) -> 'ConceptMapVersion':
    """
    Returns the specific ConceptMapVersion currently in use for normalizing data with the specified resource_type and organization
    :param resource_type:
    :param organization:
    :return:
    """
    # Load the data normalization registry
    registry_request = requests.get(f'{BASE_URL}/data_normalization/registry')
    registry_request.raise_for_status()
    registry_data = registry_request.json()

    # Filter based on resource type
    filtered_registry = [x for x in registry_data if x.get('data_element') == resource_type.value]

    # Filter to organization, if possible; default if necessary
    concept_map_uuid = None
    concept_map_version = None

    organization_specific = [x for x in filtered_registry if x.get('tenant_id') == organization.id]
    if len(organization_specific) > 0:
        concept_map_uuid = organization_specific[0].get('concept_map_uuid')
        concept_map_version = organization_specific[0].get('version')

    tenant_agnostic = [x for x in filtered_registry if x.get('tenant_id') is None]
    if len(tenant_agnostic) > 0:
        concept_map_uuid = tenant_agnostic[0].get('concept_map_uuid')
        concept_map_version  = tenant_agnostic[0].get('version')

    if concept_map_uuid is None or concept_map_version is None:
        raise Exception("No appropriate registry entry found")

    # Load the relevant concept map
    concept_map_request = requests.get(f'{BASE_URL}/ConceptMaps/', params={
        'concept_map_uuid': concept_map_uuid,
        'version': concept_map_version
    })
    concept_map_request.raise_for_status()
    return ConceptMapVersion.deserialize(concept_map_request.json())

