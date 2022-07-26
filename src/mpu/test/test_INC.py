"""Test INC instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test flag behaviour using Zeropage adressing mode ****
"""


def test_INC_flags(mpu: MPU):
    """Test DEC flags."""
    write_memory(mpu._memory, 0x1000, (0xE6, 0x20))  # INC $20
    write_memory(mpu._memory, 0x0020, (0xFE,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0

    mpu.step()
    assert mpu._memory[0x0020] == 0xFF
    assert mpu.registers.flags2str() == "Nv-bdicz"

    mpu.registers.PC = 0x1000
    mpu.step()
    assert mpu._memory[0x0020] == 0x00
    assert mpu.registers.flags2str() == "nv-bdicZ"

    mpu.registers.PC = 0x1000
    mpu.step()
    assert mpu._memory[0x0020] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"


def test_INC_zeropage(mpu: MPU):
    """Test INC zeropage."""
    write_memory(mpu._memory, 0x1000, (0xE6, 0x20))  # INC $20
    write_memory(mpu._memory, 0x0020, (0x01,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $20", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0020] == 0x02
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 5


def test_INC_zeropage_x(mpu: MPU):
    """Test INC zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xF6, 0x20))  # INC $20,X
    write_memory(mpu._memory, 0x0020, (0x00, 0x02))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $20,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0021] == 0x03
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_INC_zeropage_x_with_overflow(mpu: MPU):
    """Test INC zeropage X with overflow."""
    write_memory(mpu._memory, 0x1000, (0xF6, 0xFF))  # INC $FF,X
    write_memory(mpu._memory, 0x0000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == 0x03
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_INC_absolute(mpu: MPU):
    """Test INC absolute."""
    write_memory(mpu._memory, 0x1000, (0xEE, 0x00, 0x20))  # INC $2000
    write_memory(mpu._memory, 0x2000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == 0x03
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_INC_absolute_x(mpu: MPU):
    """Test INC absolute X."""
    write_memory(mpu._memory, 0x1000, (0xFE, 0x00, 0x20))  # INC $2000,X
    write_memory(
        mpu._memory,
        0x2000,
        (
            0x00,
            0x02,
        ),
    )
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 1
    assert mpu._memory[0x2001] == 0x03
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 7


def test_INC_absolute_x_wrapping(mpu: MPU):
    """Test INC absolute X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xFE, 0xFF, 0xFF))  # INC $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: INC $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 1
    assert mpu._memory[0x0000] == 0x03
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 8
