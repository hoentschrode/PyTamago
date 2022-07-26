"""Test CPY instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test flag behaviour using immediate adressing mode ****
"""


def test_CPY_flags(mpu: MPU):
    """Test CMP and flags."""
    # Y:Y, n:Test value
    tests = [
        # Y == n
        {"Y": 0x10, "n": 0x10, "expectedFlags": "nv-bdiCZ"},
        # Y > n
        {"Y": 0x2F, "n": 0x10, "expectedFlags": "nv-bdiCz"},
        # Y < n
        {"Y": 0x10, "n": 0x2F, "expectedFlags": "Nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xC0, test["n"]))  # CPY #$n
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload Y
        mpu.registers.Y = test["Y"]
        mpu.step()
        case_description = (
            f"Y:{format(test['Y'], '#x')}, "
            + f"n:{format(test['n'],'#x')} = {test['expectedFlags']}"
        )
        assert mpu.registers.Y == test["Y"], f"{case_description}: Y was modified."
        assert (
            mpu.registers.flags2str() == test["expectedFlags"]
        ), f"{case_description}: Flag mismatch."


"""
**** CPY adressing modes ****
"""


def test_CPY_immediate(mpu: MPU):
    """Test CPY immediate."""
    write_memory(mpu._memory, 0x1000, (0xC0, 0x34))  # CPY #$34
    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPY #$34", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 2


def test_CPY_zeropage(mpu: MPU):
    """Test CPY zeropage."""
    write_memory(mpu._memory, 0x1000, (0xC4, 0x10))  # CPY $10
    write_memory(mpu._memory, 0x0010, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPY $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 3


def test_CPY_absolute(mpu: MPU):
    """Test CPY absolute."""
    write_memory(mpu._memory, 0x1000, (0xCC, 0x00, 0x20))  # CPY $2000
    write_memory(mpu._memory, 0x2000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPY $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.Y == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4
