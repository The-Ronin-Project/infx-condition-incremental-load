from infx_condition_incremental_load.core_data_types import Organization, ResourceType
import datetime
from unittest.mock import patch
from infx_condition_incremental_load.main import load_concepts_from_errors

def generate_sample_concepts():
    """
    Each time the test is run, sample data needs to be created.
    We will use 'Test Concept [timestamp]' as the display, so it's unique every time.
    Generate two sample concepts, put them in a list
    :return:
    """
    concept1 = Concept(display=f"Test Concept {datetime.datetime.now()}")
    concept2 = Concept(display=f"Test Concept {datetime.datetime.now() + datetime.timedelta(seconds=1)}")
    return [concept1, concept2]

def test_incremental_load_integration():
    # Set up the mock error response
    organization = Organization(id='ronin')
    resource_type = ResourceType.CONDITION

    mock_data = {(organization, resource_type): generate_sample_concepts()}

    # Mock the load_concepts_from_errors function to return the mock_data
    with patch('infx_condition_incremental_load.load_concepts_from_errors',
               return_value=mock_data) as load_concepts_from_errors_mock:

    # Run the process


    # Verify new code is in code system


    # Verify new code is in value set


    # Verify new code is in concept map
