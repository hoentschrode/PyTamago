"""Test ROR operand."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using accumulator adressing mode ****
"""


def test_ROR_flags(mpu: MPU):
    """Test ROR A operation, flags and result."""
    tests = [
        {"n": 0b1000_0001, "c": False, "expectedFlags": "nv-bdiCz", "expectedValue": 0b0100_0000},
        {"n": 0b1000_0001, "c": True, "expectedFlags": "Nv-bdiCz", "expectedValue": 0b1100_0000},
        {"n": 0b0000_0001, "c": False, "expectedFlags": "nv-bdiCZ", "expectedValue": 0b0000_0000},
        {"n": 0b0100_0000, "c": False, "expectedFlags": "nv-bdicz", "expectedValue": 0b0010_0000},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x6A, 0x00))  # 1000: ROR A
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["n"]
        mpu.registers.modify_flag(Flag.CARRY, test["c"])
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"(C={1 if test['c'] else 0}) "
            + f"= {format(test['expectedValue'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedValue"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** ROR adressing modes ****
"""


def test_ROR_accumulator(mpu: MPU):
    """Test ROR accumulator."""
    write_memory(mpu._memory, 0x1000, (0x6A,))  # ROR A
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    mpu.registers.A = 0b1000_0001
    assert str(mpu.decode(0x1000)) == "1000: ROR A", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1001
    assert mpu.registers.A == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 2


def test_ROR_zeropage(mpu: MPU):
    """Test ROR zeropage."""
    write_memory(mpu._memory, 0x1000, (0x66, 0x10))  # ROR $10
    write_memory(mpu._memory, 0x0010, (0b1000_0001,))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0010] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 5


def test_ROR_zeropage_x(mpu: MPU):
    """Test ROR zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x76, 0x10))  # ROR $10,X
    write_memory(mpu._memory, 0x0013, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 3
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0013] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROR_zeropage_x_with_overflow(mpu: MPU):
    """Test ROR zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x76, 0xFF))  # ROR $ff,X
    write_memory(mpu._memory, 0x0000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROR_absolute(mpu: MPU):
    """Test ROR absolute."""
    write_memory(mpu._memory, 0x1000, (0x6E, 0x00, 0x20))  # ROR $2000
    write_memory(mpu._memory, 0x2000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROR_absolute_x(mpu: MPU):
    """Test ROR absolute X."""
    write_memory(mpu._memory, 0x1000, (0x7E, 0x00, 0x20))  # ROR $2000,X
    write_memory(mpu._memory, 0x2000, (0x00, 0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2001] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 7


def test_ROR_absolute_x_wrapping(mpu: MPU):
    """Test ROR absolute X wrapping."""
    write_memory(mpu._memory, 0x1000, (0x7E, 0xFF, 0xFF))  # ROR $FFFF,X
    write_memory(mpu._memory, 0x0000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROR $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x0000] == 0b0100_0000
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 7 + 1
