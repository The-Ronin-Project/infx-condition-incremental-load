from infx_condition_incremental_load.core_data_types import Organization, ResourceType
from infx_condition_incremental_load.terminology_resources import Concept, ConceptMapVersion, ValueSetVersion, Terminology
from infx_condition_incremental_load.main import process_errors, load_concepts_from_errors
import datetime
from unittest.mock import patch, Mock


def generate_sample_concepts():
    """
    Each time the test is run, sample data needs to be created.
    We will use 'Test Concept [timestamp]' as the display, so it's unique every time.
    Generate two sample concepts, put them in a list
    :return:
    """
    concept1 = Concept(display=f"Test Concept {datetime.datetime.now()}", code="test_concept_1")
    concept2 = Concept(display=f"Test Concept {datetime.datetime.now() + datetime.timedelta(seconds=1)}", code="test_concept_2")
    return [concept1, concept2]

def test_incremental_load_integration():
    # Set up the mock error response
    organization = Organization(id='ronin')
    resource_type = ResourceType.CONDITION

    mock_error_concept_data = {(organization, resource_type): generate_sample_concepts()}

    concept_map_uuid = 'ae61ee9b-3f55-4d3c-96e7-8c7194b53767'
    version = 1
    include_internal_info = True

    mock_registry_lookup = ConceptMapVersion.load(concept_map_uuid, version)

    # Mock the load_concepts_from_errors function to return the mock_data
    with patch('infx_condition_incremental_load.main.load_concepts_from_errors',
               return_value=mock_error_concept_data):

        with patch('infx_condition_incremental_load.main.lookup_concept_map_version_for_resource_type',
                   return_value=mock_registry_lookup):
            # Run the process
            process_errors()

    # Verify new code is in code system
    added_concepts = Terminology.load_terminology_concepts(source_terminology_uuid)
    assert len(added_concepts) == len(generate_sample_concepts)
    for concept in added_concepts:
        sample_concepts = generate_sample_concepts()
        assert concept.code in [c.code for c in sample_concepts]

    # Verify new code is in value set
    updated_value_set_version = ValueSetVersion.load(value_set_version_uuid)
    assert updated_value_set_version is not None
    assert updated_value_set_version.rules == expected_rules

    # Check that the appropriate mappings have been created or updated in the ConceptMap
    concept_map_mappings = updated_concept_map_version.load_mappings()
    for mapping in concept_map_mappings:
        assert mapping.source_concept_id in source_concept_uuids
        assert mapping.target_concept_id in target_concept_uuids

    # Check that the appropriate concepts have been added to the source terminology
    updated_concept_map_version = ConceptMapVersion.load(concept_map_version_uuid)
    assert updated_concept_map_version is not None
    assert updated_concept_map_version.mappings == expected_mappings