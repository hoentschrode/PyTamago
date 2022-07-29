"""Test ROL operand."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using accumulator adressing mode ****
"""


def test_ROL_flags(mpu: MPU):
    """Test ROL A operation, flags and result."""
    tests = [
        {"n": 0b1000_0001, "c": False, "expectedFlags": "nv-bdiCz", "expectedValue": 0b0000_0010},
        {"n": 0b1000_0001, "c": True, "expectedFlags": "nv-bdiCz", "expectedValue": 0b0000_0011},
        {"n": 0b1000_0000, "c": False, "expectedFlags": "nv-bdiCZ", "expectedValue": 0b0000_0000},
        {"n": 0b0100_0000, "c": False, "expectedFlags": "Nv-bdicz", "expectedValue": 0b1000_0000},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x2A, 0x00))  # 1000: ROL A
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
**** ROL adressing modes ****
"""


def test_ROL_accumulator(mpu: MPU):
    """Test ROL accumulator."""
    write_memory(mpu._memory, 0x1000, (0x2A,))  # ROL A
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    mpu.registers.A = 0b1000_0001
    assert str(mpu.decode(0x1000)) == "1000: ROL A", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1001
    assert mpu.registers.A == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 2


def test_ROL_zeropage(mpu: MPU):
    """Test ROL zeropage."""
    write_memory(mpu._memory, 0x1000, (0x26, 0x10))  # ROL $10
    write_memory(mpu._memory, 0x0010, (0b1000_0001,))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0010] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 5


def test_ROL_zeropage_x(mpu: MPU):
    """Test ROL zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x36, 0x10))  # ROL $10,X
    write_memory(mpu._memory, 0x0013, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 3
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0013] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROL_zeropage_x_with_overflow(mpu: MPU):
    """Test ROL zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x36, 0xFF))  # ROL $ff,X
    write_memory(mpu._memory, 0x0000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROL_absolute(mpu: MPU):
    """Test ROL absolute."""
    write_memory(mpu._memory, 0x1000, (0x2E, 0x00, 0x20))  # ROL $2000
    write_memory(mpu._memory, 0x2000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 6


def test_ROL_absolute_x(mpu: MPU):
    """Test ROL absolute X."""
    write_memory(mpu._memory, 0x1000, (0x3E, 0x00, 0x20))  # ROL $2000,X
    write_memory(mpu._memory, 0x2000, (0x00, 0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2001] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 7


def test_ROL_absolute_x_wrapping(mpu: MPU):
    """Test ROL absolute X wrapping."""
    write_memory(mpu._memory, 0x1000, (0x3E, 0xFF, 0xFF))  # ROL $FFFF,X
    write_memory(mpu._memory, 0x0000, (0b1000_0001, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: ROL $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x0000] == 0b0000_0010
    assert mpu.registers.CARRY
    assert mpu.elapsed_cycles == 7 + 1
