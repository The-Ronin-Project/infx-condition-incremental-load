from infx_condition_incremental_load.core_data_types import Organization, ResourceType
from infx_condition_incremental_load.terminology_resources import Concept, ConceptMapVersion
from infx_condition_incremental_load.main import process_errors, load_concepts_from_errors
import datetime
from unittest.mock import patch

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
               return_value=mock_error_concept_data) as load_concepts_from_errors_mock:

        with patch('infx_condition_incremental_load.terminology_resources.lookup_concept_map_version_for_resource_type',
                   return_value=mock_registry_lookup) as lookup_concept_map_version_for_resource_type_mock:
            # Run the process
            process_errors()

    # Verify new code is in code system
    added_concepts = load_concepts_from_source_terminology(source_terminology_uuid)
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



# You will need to implement a mock function to simulate the error loading process
def mock_load_errors(errors):
    # This function should return the provided errors
    return errors


# Test case 1: No errors
def test_load_concepts_from_errors_no_errors():
    errors = []
    load_errors_mock = Mock(side_effect=mock_load_errors(errors))

    result = load_concepts_from_errors(load_errors_mock)

    assert result == {}


# Test case 2: Errors with different organizations and resource types
def test_load_concepts_from_errors_different_orgs_and_resource_types():
    errors = [
        # Your error objects with concepts from different organizations and resource types
    ]
    load_errors_mock = Mock(side_effect=mock_load_errors(errors))

    result = load_concepts_from_errors(load_errors_mock)

    # You will need to update the expected_result dictionary based on the concepts in your error objects
    expected_result = {
        # Tuple (Organization, ResourceType): List of Concepts
    }

    assert result == expected_result


# Test case 3: Errors with multiple concepts for the same organization and resource type
def test_load_concepts_from_errors_multiple_concepts_same_org_and_resource_type():
    errors = [
        # Your error objects with multiple concepts for the same organization and resource type
    ]
    load_errors_mock = Mock(side_effect=mock_load_errors(errors))

    result = load_concepts_from_errors(load_errors_mock)

    # You will need to update the expected_result dictionary based on the concepts in your error objects
    expected_result = {
        # Tuple (Organization, ResourceType): List of Concepts
    }

    assert result == expected_result


# Test case 4: Errors with invalid data
def test_load_concepts_from_errors_invalid_data():
    errors = [
        # Your error objects with invalid data
    ]
    load_errors_mock = Mock(side_effect=mock_load_errors(errors))

    with pytest.raises(Exception):
        load_concepts_from_errors(load_errors_mock)


# You will need to implement a mock function to simulate the registry lookup process
def mock_registry_lookup(resource_type, organization, registry_entries):
    # This function should return the matching registry entry or None if not found
    return next((entry for entry in registry_entries if
                 entry['resource_type'] == resource_type and entry['organization'] == organization), None)


# Test case 1: No registry entry found for the given resource type and organization
def test_lookup_concept_map_version_for_resource_type_no_registry_entry():
    organization = Organization(id='test_org')
    resource_type = ResourceType.PROCEDURE
    registry_entries = [
        # Your registry entries without a matching entry for the given resource_type and organization
    ]
    registry_lookup_mock = Mock(side_effect=lambda rt, org: mock_registry_lookup(rt, org, registry_entries))

    with pytest.raises(Exception):
        lookup_concept_map_version_for_resource_type(resource_type, organization, registry_lookup_mock)

    # Test case 2: Registry entry found for the given resource type but not for the specific organization


def test_lookup_concept_map_version_for_resource_type_different_organization():
    organization = Organization(id='test_org')
    resource_type = ResourceType.PROCEDURE
    registry_entries = [
        # Your registry entries with a matching entry for the given resource_type but not for the specific organization
    ]
    registry_lookup_mock = Mock(side_effect=lambda rt, org: mock_registry_lookup(rt, org, registry_entries))

    with pytest.raises(Exception):
        lookup_concept_map_version_for_resource_type(resource_type, organization, registry_lookup_mock)

    # Test case 3: Multiple registry entries found for the same resource type and organization


def test_lookup_concept_map_version_for_resource_type_multiple_entries():
    organization = Organization(id='test_org')
    resource_type = ResourceType.PROCEDURE
    registry_entries = [
        # Your registry entries with multiple matching entries for the given resource_type and organization
    ]
    registry_lookup_mock = Mock(side_effect=lambda rt, org: mock_registry_lookup(rt, org, registry_entries))

    with pytest.raises(Exception):
        lookup_concept_map_version_for_resource_type(resource_type, organization, registry_lookup_mock)



# Test case 1: new_version with different input descriptions
def test_new_version_with_different_input_descriptions():
    value_set_version = ValueSetVersion()
    description1 = "New version for ICD-10 update"
    description2 = "New version for SNOMED CT update"

    new_version1 = value_set_version.new_version(description1)
    new_version2 = value_set_version.new_version(description2)

    assert new_version1.description == description1
    assert new_version2.description == description2


# Test case 2: update_rules_for_new_terminology_version with different input old and new terminology version UUIDs
def test_update_rules_for_new_terminology_version_with_different_input_old_and_new_terminology_version_uuids():
    value_set_version = ValueSetVersion()
    old_terminology_version_uuid = "11111111-1111-1111-1111-111111111111"
    new_terminology_version_uuid = "22222222-2222-2222-2222-222222222222"

    # You may need to set up some initial rules for the value_set_version using the old_terminology_version_uuid

    value_set_version.update_rules_for_new_terminology_version(old_terminology_version_uuid,
                                                               new_terminology_version_uuid)

    # Assert that the rules have been updated with the new_terminology_version_uuid
    # This will depend on how your rules are stored in the value_set_version object


# Test case 3: publish with different value set versions (published and unpublished)
def test_publish_with_different_value_set_versions():
    value_set_version_published = ValueSetVersion()
    value_set_version_unpublished = ValueSetVersion()

    # Set the published status for the value_set_version_published object
    value_set_version_published.published = True

    value_set_version_published.publish()
    value_set_version_unpublished.publish()

    # Assert that both value_set_version_published and value_set_version_unpublished are published after calling the publish method
    assert value_set_version_published.published == True
    assert value_set_version_unpublished.published == True


# Test case 1: new_version with different input parameters
def test_new_version_with_different_input_parameters():
    concept_map_version = ConceptMapVersion()
    input_parameters1 = {"description": "New version for ICD-10 to SNOMED CT mapping update"}
    input_parameters2 = {"description": "New version for LOINC to SNOMED CT mapping update"}

    new_version1 = concept_map_version.new_version(**input_parameters1)
    new_version2 = concept_map_version.new_version(**input_parameters2)

    assert new_version1.description == input_parameters1["description"]
    assert new_version2.description == input_parameters2["description"]


# Test case 2: publish with different concept map versions (published and unpublished)
def test_publish_with_different_concept_map_versions():
    concept_map_version_published = ConceptMapVersion()
    concept_map_version_unpublished = ConceptMapVersion()

    # Set the published status for the concept_map_version_published object
    concept_map_version_published.published = True

    concept_map_version_published.publish()
    concept_map_version_unpublished.publish()

    # Assert that both concept_map_version_published and concept_map_version_unpublished are published after calling the publish method
    assert concept_map_version_published.published == True
    assert concept_map_version_unpublished.published == True


# You will need to implement a mock function to simulate the concept loading process
def mock_load_concepts(errors):
    # This function should return the provided concepts
    return load_concepts_from_errors(errors)


# Test case 1: Errors with unsupported resource type
def test_process_errors_unsupported_resource_type():
    errors = [
        # Your error objects with unsupported resource type
        {"error_type": ErrorType.UNSUPPORTED_RESOURCE_TYPE, "organization": Organization(id='test_org'),
         "resource_type": ResourceType.UNKNOWN}
    ]
    load_concepts_mock = Mock(side_effect=mock_load_concepts(errors))

    with pytest.raises(Exception):
        process_errors(load_concepts_mock)

    # Test case 2: Errors with unsupported organization


def test_process_errors_unsupported_organization():
    errors = [
        # Your error objects with unsupported organization
        {"error_type": ErrorType.UNSUPPORTED_ORGANIZATION, "organization": Organization(id='unknown_org'),
         "resource_type": ResourceType.CONDITION}
    ]
    load_concepts_mock = Mock(side_effect=mock_load_concepts(errors))

    with pytest.raises(Exception):
        process_errors(load_concepts_mock)

    # Test case 3: Errors with invalid concept data


def test_process_errors_invalid_concept_data():
    errors = [
        # Your error objects with invalid concept data
        {"error_type": ErrorType.INVALID_CONCEPT_DATA, "organization": Organization(id='test_org'),
         "resource_type": ResourceType.CONDITION, "invalid_data": "Invalid concept data example"}
    ]
    load_concepts_mock = Mock(side_effect=mock_load_concepts(errors))

    with pytest.raises(Exception):
        process_errors(load_concepts_mock)

    # Test case 4: Errors with database connection issues


def test_process_errors_database_connection_issues():
    errors = [
        # Your error objects with database connection issues
        {"error_type": ErrorType.DATABASE_CONNECTION_ISSUE, "organization": Organization(id='test_org'),
         "resource_type": ResourceType.CONDITION}
    ]
    load_concepts_mock = Mock(side_effect=mock_load_concepts(errors))

    with pytest.raises(Exception):
        process_errors(load_concepts_mock)
