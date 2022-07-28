"""Test LDY instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using immediate adressing mode ****
"""


def test_LDY_flags(mpu: MPU):
    """Test LDY flag."""
    tests = [
        {"Y": 0x00, "expectedFlags": "nv-bdicZ"},
        {"Y": 0x01, "expectedFlags": "nv-bdicz"},
        {"Y": 0xFF, "expectedFlags": "Nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xA0, test["Y"]))  # LDY #$x
        mpu.registers.Y = 0x10
        mpu.registers.PC = 0x1000
        mpu.step()
        assert mpu.registers.Y == test["Y"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_LDY_immediate(mpu: MPU):
    """Test LDY immediate."""
    write_memory(mpu._memory, 0x1000, (0xA0, 0x12))  # 1000: LDY #$12

    mpu.registers.PC = 0x1000
    assert mpu.registers.Y == 0
    assert str(mpu.decode(0x1000)) == "1000: LDY #$12", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 2


def test_LDY_zeropage(mpu: MPU):
    """Test LDY zeropage."""
    write_memory(mpu._memory, 0x1000, (0xA4, 0x10))  # 1000: LDY $10
    write_memory(mpu._memory, 0x0010, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDY $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 3


def test_LDY_zeropage_x(mpu: MPU):
    """Test LDY zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xB4, 0x10))  # 1000: LDY $10,X
    write_memory(mpu._memory, 0x0013, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.Y = 0x00
    assert str(mpu.decode(0x1000)) == "1000: LDY $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDY_zeropage_x_with_overflow(mpu: MPU):
    """Test LDY zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0xB4, 0xFF))  # 1000: LDY $FF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.Y = 0x00
    assert str(mpu.decode(0x1000)) == "1000: LDY $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDY_absolute(mpu: MPU):
    """Test LDY absolute."""
    write_memory(mpu._memory, 0x1000, (0xAC, 0x00, 0x20))  # 1000: LDY $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDY $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDY_absolute_x(mpu: MPU):
    """Test LDY absolute X."""
    write_memory(mpu._memory, 0x1000, (0xBC, 0x00, 0x20))  # 1000: LDY $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDY $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.Y == 0x34
    assert mpu.elapsed_cycles == 4


def test_LDY_absolute_x_wrapping(mpu: MPU):
    """Test LDY absolute x full wrapping."""
    write_memory(mpu._memory, 0x1000, (0xBC, 0xFF, 0xFF))  # 1000: LDY $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDY $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.Y == 0x12
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."
