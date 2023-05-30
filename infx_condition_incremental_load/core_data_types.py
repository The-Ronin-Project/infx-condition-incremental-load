from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    MEDICATION = "Medication"
    TELECOM_USE = "Practitioner.telecom.use"  # Only in for testing until we have a real data type live


@dataclass
class Organization:
    id: str