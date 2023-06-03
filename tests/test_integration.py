from infx_condition_incremental_load.core_data_types import Organization, ResourceType
from infx_condition_incremental_load.terminology_resources import Concept, ConceptMapVersion, ValueSetVersion, \
    Terminology
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
    concept1 = Concept(
        display=f"Test Concept {datetime.datetime.now()}",
        code="test_concept_1",
        system='http://projectronin.io/fhir/CodeSystem/mock/condition',
        version='1.0'
    )
    concept2 = Concept(
        display=f"Test Concept {datetime.datetime.now() + datetime.timedelta(seconds=1)}",
        code="test_concept_2",
        system='http://projectronin.io/fhir/CodeSystem/mock/condition',
        version='1.0'
    )
    return [concept1, concept2]


def test_incremental_load_integration():
    # Set up the mock error response
    # Creating a mock organization object
    organization = Organization(id='ronin')
    # Specifying the resource type as CONDITION
    resource_type = ResourceType.CONDITION

    # Generating a sample set of concepts and associating them with the above organization and resource type
    mock_error_concept_data = {(organization, resource_type): generate_sample_concepts()}

    # Creating identifiers for concept map and version to use in mock function
    concept_map_uuid = 'ae61ee9b-3f55-4d3c-96e7-8c7194b53767'
    version = 1
    include_internal_info = True

    # Creating a mock response for ConceptMapVersion.load method
    mock_registry_lookup = ConceptMapVersion.load(concept_map_uuid, version)

    # Mock the load_concepts_from_errors function to return the mock_data
    # Using Python's mock patching mechanism to replace the original 'load_concepts_from_errors' function
    # The function will return the mock data instead of executing the original code
    with patch('infx_condition_incremental_load.main.load_concepts_from_errors',
               return_value=mock_error_concept_data):

        # Similar to the above, we are mocking the 'lookup_concept_map_version_for_resource_type' function
        # It will return the 'mock_registry_lookup' instead of executing the original code
        with patch('infx_condition_incremental_load.main.lookup_concept_map_version_for_resource_type',
                   return_value=mock_registry_lookup):
            # Calling the process_errors function, which should use our mock data and functions
            process_errors()

    # # After running the process, we want to check if the code system has the new concepts
    # # Load the added concepts from the terminology
    # added_concepts = Terminology.load_terminology_concepts(source_terminology_uuid)
    # # Assert that the number of added concepts matches the number of concepts in the sample data
    # assert len(added_concepts) == len(generate_sample_concepts)
    # # Check if every concept in added concepts exists in the sample concepts
    # for concept in added_concepts:
    #     sample_concepts = generate_sample_concepts()
    #     assert concept.code in [c.code for c in sample_concepts]
    #
    # # Loading the updated version of the value set
    # updated_value_set_version = ValueSetVersion.load(value_set_version_uuid)
    # # Assert that the updated value set version exists
    # assert updated_value_set_version is not None
    # # Check if the rules in the updated version match the expected rules
    # assert updated_value_set_version.rules == expected_rules
    #
    # # Loading the mappings from the concept map version
    # concept_map_mappings = updated_concept_map_version.load_mappings()
    # # Check if the source and target concept ids in each mapping exist in the source and target concept uuids
    # for mapping in concept_map_mappings:
    #     assert mapping.source_concept_id in source_concept_uuids
    #     assert mapping.target_concept_id in target_concept_uuids
    #
    # # Loading the updated version of the concept map
    # updated_concept_map_version = ConceptMapVersion.load(concept_map_version_uuid)
    # # Assert that the updated concept map version exists
    # assert updated_concept_map_version is not None
    # # Check if the mappings in the updated version match the expected mappings
    # assert updated_concept_map_version.mappings == expected_mappings