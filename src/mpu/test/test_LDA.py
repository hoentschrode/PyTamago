"""Test LDA instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_LDA_immediate(mpu: MPU):
    """Test LDA immediate."""
    write_memory(mpu._memory, 0x1000, (0xA9, 0x12))  # 1000: LDA #$12

    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: LDA #$12", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.ZERO is False
    assert mpu.registers.NEGATIVE is False
    assert mpu.elapsed_cycles == 2


def test_LDA_immediate_sets_n_flag(mpu: MPU):
    """Test LDA immediate N+."""
    write_memory(mpu._memory, 0x1000, (0xA9, 0x80))  # 1000: LDA #$80

    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: LDA #$80", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x80
    assert mpu.registers.NEGATIVE is True
    assert mpu.registers.ZERO is False
    assert mpu.elapsed_cycles == 2


def test_LDA_immediate_sets_z_flag(mpu: MPU):
    """Test LDA immediate Z+."""
    write_memory(mpu._memory, 0x1000, (0xA9, 0x00))  # 1000: LDA #$00

    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: LDA #$00", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x00
    assert mpu.registers.NEGATIVE is False
    assert mpu.registers.ZERO is True
    assert mpu.elapsed_cycles == 2


def test_LDA_zeropage(mpu: MPU):
    """Test LDA zeropage."""
    write_memory(mpu._memory, 0x1000, (0xA5, 0x10))  # 1000: LDA $10
    write_memory(mpu._memory, 0x0010, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDA $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 3


def test_LDA_zeropage_x(mpu: MPU):
    """Test LDA zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xB5, 0x10))  # 1000: LDA $10,X
    write_memory(mpu._memory, 0x0013, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    assert str(mpu.decode(0x1000)) == "1000: LDA $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDA_zeropage_x_with_overflow(mpu: MPU):
    """Test LDA zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0xB5, 0xFF))  # 1000: LDA $FF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    assert str(mpu.decode(0x1000)) == "1000: LDA $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDA_absolute(mpu: MPU):
    """Test LDA absolute."""
    write_memory(mpu._memory, 0x1000, (0xAD, 0x00, 0x20))  # 1000: LDA $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: LDA $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_LDA_absolute_x(mpu: MPU):
    """Test LDA absolute X."""
    write_memory(mpu._memory, 0x1000, (0xBD, 0x00, 0x20))  # 1000: LDA $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 4


def test_LDA_absolute_x_wrapping(mpu: MPU):
    """Test LDA absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0xBD, 0xFF, 0xFF))  # 1000: LDA $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_LDA_absolute_y(mpu: MPU):
    """Test LDA absolute Y."""
    write_memory(mpu._memory, 0x1000, (0xB9, 0x00, 0x20))  # 1000: LDA $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 4


def test_LDA_absolute_y_wrapping(mpu: MPU):
    """Test LDA absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0xB9, 0xFF, 0xFF))  # 1000: LDA $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4 + 1


def test_LDA_indirect_x(mpu: MPU):
    """Test LDA indirect X."""
    write_memory(mpu._memory, 0x1000, (0xA1, 0x12))  # 1000: LDA ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 6


def test_LDA_indirect_x_wrapping(mpu: MPU):
    """Test LDA indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xA1, 0xFE))  # 1000: LDA ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 6


def test_LDA_indirect_y(mpu: MPU):
    """Test LDA indirect Y."""
    write_memory(mpu._memory, 0x1000, (0xB1, 0x12))  # 1000: LDA ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 5


def test_LDA_indirect_y_wrapping(mpu: MPU):
    """Test LDA indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xB1, 0xFF))  # 1000: LDA ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: LDA ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 5 + 1
