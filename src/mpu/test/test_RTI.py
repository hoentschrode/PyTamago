"""Test RTI instruction."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_RTI(mpu: MPU):
    """Test BRK."""
    write_memory(mpu._memory, 0x1000, (0x40,))  # 1000: RTI
    # Prepare stack
    write_memory(
        mpu._memory, 0x01FD, (Flag.CARRY.value | Flag.ZERO.value, 0x00, 0x20)
    )  # flags, pcl, pch
    mpu.registers.SP = 0xFC
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: RTI", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x2000, "PC not pointing to return address."
    assert mpu.registers.flags2str() == "nv-bdiCZ"
    # Analyse stack
    assert mpu.registers.SP == 0xFF, "Stack not shrunk by 3 byte."
