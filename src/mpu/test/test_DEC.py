"""Test DEC instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test flag behaviour using Zeropage adressing mode ****
"""


def test_DEC_flags(mpu: MPU):
    """Test DEC flags."""
    write_memory(mpu._memory, 0x1000, (0xC6, 0x20))  # DEC $20
    write_memory(mpu._memory, 0x0020, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0

    mpu.step()
    assert mpu._memory[0x0020] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"

    mpu.registers.PC = 0x1000
    mpu.step()
    assert mpu._memory[0x0020] == 0x00
    assert mpu.registers.flags2str() == "nv-bdicZ"

    mpu.registers.PC = 0x1000
    mpu.step()
    assert mpu._memory[0x0020] == 0xFF
    assert mpu.registers.flags2str() == "Nv-bdicz"


def test_DEC_zeropage(mpu: MPU):
    """Test DEC zeropage."""
    write_memory(mpu._memory, 0x1000, (0xC6, 0x20))  # DEC $20
    write_memory(mpu._memory, 0x0020, (0x01,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: DEC $20", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0020] == 0
    assert mpu.registers.flags2str() == "nv-bdicZ"
    assert mpu.elapsed_cycles == 5


def test_DEC_zeropage_x(mpu: MPU):
    """Test DEC zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xD6, 0x20))  # DEC $20,X
    write_memory(mpu._memory, 0x0020, (0x00, 0x02))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: DEC $20,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0021] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_DEC_zeropage_x_with_overflow(mpu: MPU):
    """Test DEC zeropage X with overflow."""
    write_memory(mpu._memory, 0x1000, (0xD6, 0xFF))  # DEC $FF,X
    write_memory(mpu._memory, 0x0000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: DEC $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_DEC_absolute(mpu: MPU):
    """Test DEC absolute."""
    write_memory(mpu._memory, 0x1000, (0xCE, 0x00, 0x20))  # DEC $2000
    write_memory(mpu._memory, 0x2000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: DEC $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_DEC_absolute_x(mpu: MPU):
    """Test DEC absolute X."""
    write_memory(mpu._memory, 0x1000, (0xDE, 0x00, 0x20))  # DEC $2000,X
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
    assert str(mpu.decode(0x1000)) == "1000: DEC $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 1
    assert mpu._memory[0x2001] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 7


def test_DEC_absolute_x_wrapping(mpu: MPU):
    """Test DEC absolute X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xDE, 0xFF, 0xFF))  # DEC $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x02,))
    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.FLAGS = 0
    assert str(mpu.decode(0x1000)) == "1000: DEC $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.X == 1
    assert mpu._memory[0x0000] == 0x01
    assert mpu.registers.flags2str() == "nv-bdicz"
    assert mpu.elapsed_cycles == 8
