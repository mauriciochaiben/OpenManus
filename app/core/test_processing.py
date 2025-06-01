"""Test file to verify execution."""

print("Starting execution")

import re

print("re imported")

from typing import Any, Dict, List, Optional

print("typing imported")

from dataclasses import dataclass

print("dataclass imported")

import logging

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
