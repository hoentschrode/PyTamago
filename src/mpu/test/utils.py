"""Test utility functions."""
from typing import List


def write_memory(memory: List[int], address: int, bytes):
    """Write one or more bytes into memory."""
    memory[address : address + len(bytes)] = bytes
