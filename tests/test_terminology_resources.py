import pytest
from unittest.mock import Mock
from infx_condition_incremental_load.terminology_resources import *

# Assume that you have the following imports at the top of your test module
# from your_module import lookup_concept_map_version_for_resource_type, ResourceType


def test_lookup_concept_map_version_for_resource_type():
    # Arrange
    organization = Organization(id='ronin')
    resource_type = ResourceType.TELECOM_USE

    # For this mock ConceptMapVersion object, you'll need to customize this to fit
    # what the actual ConceptMapVersion object would look like.
    expected_concept_map_version = Mock()
    expected_concept_map_version.uuid = "f0d5d977-5cfd-43d3-8c74-5c01e51dca27"

    # Assuming you have a mockable function to get the ConceptMapVersion
    # you'll want to set it up here. This will depend on how your
    # function is implemented
    # e.g.
    # with patch('your_module.get_concept_map_version') as mock_get:
    #    mock_get.return_value = expected_concept_map_version

    # Act
    result = lookup_concept_map_version_for_resource_type(resource_type, organization)

    # Assert
    assert result.uuid == expected_concept_map_version.uuid
    # Additionally, you can assert that the expected methods were called on the
    # Organization object, or other assertions as necessary depending on your
    # function's implementation.


def test_load_value_set_version():
    BREAST_CANCER_SURVEY_ASSIGNMENT_UUID = "83b23149-b24a-4a7a-91e0-844fee1dd3b6"
    value_set_version = ValueSetVersion.load(BREAST_CANCER_SURVEY_ASSIGNMENT_UUID)

    assert value_set_version.title == "Breast Cancer Survey Assignment"
    terminologies = value_set_version.lookup_terminologies_in_value_set_version()

    assert len(terminologies) == 2

    # Sort the terminologies by fhir_uri to ensure a consistent order
    terminologies.sort(key=lambda t: t.fhir_uri)

    terminology1, terminology2 = terminologies

    assert terminology1.version == "2023"
    assert terminology1.fhir_uri == "http://hl7.org/fhir/sid/icd-10-cm"
    assert terminology2.version == "2023-03-01"
    assert terminology2.fhir_uri == "http://snomed.info/sct"
