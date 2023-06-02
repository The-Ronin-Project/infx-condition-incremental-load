from typing import List, Dict, Tuple
from enum import Enum
from uuid import UUID

from infx_condition_incremental_load.terminology_resources import *
from infx_condition_incremental_load.core_data_types import *


# This process needs to be handled in batches, so we don't create unnecessary versions of terminologies, value sets, concept maps, etc.
# Batches should be broken up by organization id and resource type


def load_concepts_from_errors() -> Dict[Tuple[Organization, ResourceType], List[Concept]]:
    """
   Loads and processes a list of errors to extract specific concepts from them.

   This function parses each error and identifies the relevant concepts. These concepts are
   then grouped by the originating organization and the type of resource they belong to. The
   results are returned as a dictionary, where each key is a tuple of an organization and a
   resource type, and each value is a list of concepts associated with that key.

   Returns:
       Dict[Tuple[Organization, ResourceType], List[Concept]]: A dictionary mapping tuples of
       organization and resource type to lists of concepts extracted from the errors.
   """
    pass


# def lookup_source_target_value_sets_for_concept_map(concept_map_uuid:UUID) -> Tuple['ValueSet', 'ValueSet']:
#     pass


def process_errors():
    concepts_to_load = load_concepts_from_errors()

    for key, concept_list in concepts_to_load.items():
        organization, resource_type = key

        concept_map_version = lookup_concept_map_version_for_resource_type(
            resource_type=resource_type,
            organization=organization
        )

        source_value_set_version = concept_map_version.source_value_set_version
        target_value_set_version = concept_map_version.target_value_set_version

        # verify source and target value set versions are the latest versions

        source_response = requests.get(f"{base_url}/ValueSets/{source_identifier}/most_recent_active_version")
        target_response = requests.get(f"{base_url}/ValueSets/{target_identifier}/most_recent_active_version")

        if source_response.status_code == 200 and target_response.status_code == 200:
            latest_source_version = source_response.json()
            latest_target_version = target_response.json()

            # Check if the given versions match the latest versions
            return (
                    source_value_set_version.uuid == latest_source_version["uuid"]
                    and target_value_set_version.uuid == latest_target_version["uuid"]
            )

        return False

            # Ensure only one terminology is used in the source value set
        # Otherwise, we can't determine where to automatically load the new codes
        source_terminologies = source_value_set_version.lookup_terminologies_in_value_set_version()

        if len(source_terminologies) > 1:
            raise Exception('Multiple terminologies in source value set; cannot automatically add codes')

        source_terminology = source_terminologies[0]

        # Add new codes to terminology
        # todo: implement logic to create new terminology version, if necessary
        new_terminology_version = False
        try:
            source_terminology.load_additional_concepts(concept_list)
        except Exception as e:
            new_terminology_version = True
            raise e

        # todo: Create new value set version
        new_source_value_set_version = source_value_set_version.new_version("new version created by the condition incremental load system")

        if new_terminology_version:
            new_source_value_set_version.update_rules_for_new_terminology_version(    # todo: only applicable if you had to create a new terminology version
                old_terminology_version_uuid=None,
                new_terminology_version_uuid=None
            )

        # todo: Publish new value set version
        new_source_value_set_version.publish()

        # todo: Create new concept map version
        new_concept_map_version = concept_map_version.new_version()

        # todo: register new data in appropriate queue for triaging