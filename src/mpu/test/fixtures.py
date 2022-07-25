"""Fixture definitions."""
import pytest
from mpu.mpu6502 import MPU


@pytest.fixture
def mpu() -> MPU:
    memory = [0x00] * (0xFFFF + 1)
    mpu = MPU(memory=memory, pc=0)
    return mpu
