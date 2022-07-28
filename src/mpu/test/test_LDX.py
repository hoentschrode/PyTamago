"""Test LDX instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using immediate adressing mode ****
"""


def test_LDX_flags(mpu: MPU):
    """Test LDX flag."""
    tests = [
        {"X": 0x00, "expectedFlags": "nv-bdicZ"},
        {"X": 0x01, "expectedFlags": "nv-bdicz"},
        {"X": 0xFF, "expectedFlags": "Nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xA2, test["X"]))  # LDX #$x
        mpu.registers.X = 0x10
        mpu.registers.PC = 0x1000
        mpu.step()
        assert mpu.registers.X == test["X"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_LDX_immediate(mpu: MPU):
    """Test LDX immediate."""
    write_memory(mpu._memory, 0x1000, (0xA2, 0x12))  # 1000: LDX #$12

    mpu.registers.PC = 0x1000
    assert mpu.registers.X == 0
    assert str(mpu.decode(0x1000)) == "1000: LDX #$12", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 2


def test_LDX_zeropage(mpu: MPU):
    """Test LDX zeropage."""
    write_memory(mpu._memory, 0x1000, (0xA6, 0x10))  # 1000: LDX $10
    write_memory(mpu._memory, 0x0010, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDX $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 3


def test_LDX_zeropage_y(mpu: MPU):
    """Test LDX zeropage Y."""
    write_memory(mpu._memory, 0x1000, (0xB6, 0x10))  # 1000: LDX $10,Y
    write_memory(mpu._memory, 0x0013, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x00
    mpu.registers.Y = 0x03
    assert str(mpu.decode(0x1000)) == "1000: LDX $10,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDX_zeropage_y_with_overflow(mpu: MPU):
    """Test LDA zeropage Y overflow."""
    write_memory(mpu._memory, 0x1000, (0xB6, 0xFF))  # 1000: LDX $FF,Y
    write_memory(mpu._memory, 0x0000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x00
    mpu.registers.Y = 0x01
    assert str(mpu.decode(0x1000)) == "1000: LDX $FF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDX_absolute(mpu: MPU):
    """Test LDX absolute."""
    write_memory(mpu._memory, 0x1000, (0xAE, 0x00, 0x20))  # 1000: LDX $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDX $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDX_absolute_y(mpu: MPU):
    """Test LDX absolute Y."""
    write_memory(mpu._memory, 0x1000, (0xBE, 0x00, 0x20))  # 1000: LDX $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDX $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 0x34
    assert mpu.elapsed_cycles == 4


def test_LDX_absolute_y_wrapping(mpu: MPU):
    """Test LDX absolute Y full wrapping."""
    write_memory(mpu._memory, 0x1000, (0xBE, 0xFF, 0xFF))  # 1000: LDX $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDX $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 0x12
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."
