"""Test STA instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_STA_zeropage(mpu: MPU):
    """Test STD zeropage."""
    write_memory(mpu._memory, 0x1000, (0x85, 0x10))  # 1000: STA $10
    write_memory(mpu._memory, 0x0010, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0010] == mpu.registers.A
    assert mpu.elapsed_cycles == 3


def test_STA_zeropage_x(mpu: MPU):
    """Test STA zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x95, 0x10))  # 1000: STA $10,X
    write_memory(mpu._memory, 0x0013, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0013] == mpu.registers.A
    assert mpu.elapsed_cycles == 4


def test_STA_zeropage_x_with_overflow(mpu: MPU):
    """Test STA zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x95, 0xFF))  # 1000: STA $FF,X
    write_memory(mpu._memory, 0x0000, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == mpu.registers.A
    assert mpu.elapsed_cycles == 4


def test_STA_absolute(mpu: MPU):
    """Test STA absolute."""
    write_memory(mpu._memory, 0x1000, (0x8D, 0x00, 0x20))  # 1000: STA $2000
    write_memory(mpu._memory, 0x2000, (0x00, 0x00, 0x00))
    mpu.registers.A = 0x1F
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: STA $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == mpu.registers.A
    assert mpu.elapsed_cycles == 4


def test_STA_absolute_x(mpu: MPU):
    """Test STA absolute X."""
    write_memory(mpu._memory, 0x1000, (0x9D, 0x00, 0x20))  # 1000: STA $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2001] == mpu.registers.A
    assert mpu.elapsed_cycles == 4


def test_STA_absolute_x_wrapping(mpu: MPU):
    """Test STA absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0x9D, 0xFF, 0xFF))  # 1000: STA $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x0000] == mpu.registers.A
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_STA_absolute_y(mpu: MPU):
    """Test STA absolute Y."""
    write_memory(mpu._memory, 0x1000, (0x99, 0x00, 0x20))  # 1000: STA $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2001] == mpu.registers.A
    assert mpu.elapsed_cycles == 4


def test_STA_absolute_y_wrapping(mpu: MPU):
    """Test STA absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0x99, 0xFF, 0xFF))  # 1000: STA $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x0000] == mpu.registers.A
    assert mpu.elapsed_cycles == 4 + 1


def test_STA_indirect_x(mpu: MPU):
    """Test STA indirect X."""
    write_memory(mpu._memory, 0x1000, (0x81, 0x12))  # 1000: LDA ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x2000] == mpu.registers.A
    assert mpu.elapsed_cycles == 6


def test_STA_indirect_x_wrapping(mpu: MPU):
    """Test STA indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x81, 0xFE))  # 1000: LDA ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x2000] == mpu.registers.A
    assert mpu.elapsed_cycles == 6


def test_STA_indirect_y(mpu: MPU):
    """Test STA indirect Y."""
    write_memory(mpu._memory, 0x1000, (0x91, 0x12))  # 1000: STA ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x2001] == mpu.registers.A
    assert mpu.elapsed_cycles == 5


def test_STA_indirect_y_wrapping(mpu: MPU):
    """Test STA indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x91, 0xFF))  # 1000: STA ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STA ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x2100] == mpu.registers.A
    assert mpu.elapsed_cycles == 5 + 1
