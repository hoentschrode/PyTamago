"""Test CPX instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test flag behaviour using immediate adressing mode ****
"""


def test_CPX_flags(mpu: MPU):
    """Test CMP and flags."""
    # X:X, n:Test value
    tests = [
        # X == n
        {"X": 0x10, "n": 0x10, "expectedFlags": "nv-bdiCZ"},
        # X > n
        {"X": 0x2F, "n": 0x10, "expectedFlags": "nv-bdiCz"},
        # X < n
        {"X": 0x10, "n": 0x2F, "expectedFlags": "Nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xE0, test["n"]))  # CPX #$n
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload X
        mpu.registers.X = test["X"]
        mpu.step()
        case_description = (
            f"X:{format(test['X'], '#x')}, "
            + f"n:{format(test['n'],'#x')} = {test['expectedFlags']}"
        )
        assert mpu.registers.X == test["X"], f"{case_description}: X was modified."
        assert (
            mpu.registers.flags2str() == test["expectedFlags"]
        ), f"{case_description}: Flag mismatch."


"""
**** CPX adressing modes ****
"""


def test_CPX_immediate(mpu: MPU):
    """Test CPX immediate."""
    write_memory(mpu._memory, 0x1000, (0xE0, 0x34))  # CPX #$34
    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPX #$34", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 2


def test_CPX_zeropage(mpu: MPU):
    """Test CPX zeropage."""
    write_memory(mpu._memory, 0x1000, (0xE4, 0x10))  # CPX $10
    write_memory(mpu._memory, 0x0010, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPX $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 3


def test_CPX_absolute(mpu: MPU):
    """Test CPX absolute."""
    write_memory(mpu._memory, 0x1000, (0xEC, 0x00, 0x20))  # CPX $2000
    write_memory(mpu._memory, 0x2000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CPX $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4
