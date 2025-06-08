"""Test file to verify execution."""

from dataclasses import dataclass
import logging

print("Starting execution")
print("re imported")
print("typing imported")
print("dataclass imported")
print("logging imported")

logger = logging.getLogger(__name__)
print("logger created")


@dataclass
class TestChunk:
    id: str
    content: str


print("dataclass defined")


class TestProcessor:
    def __init__(self):
        self.name = "test"


print("class defined")
print("End of execution")
