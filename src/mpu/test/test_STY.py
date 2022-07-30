"""Test STY instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_STY_zeropage(mpu: MPU):
    """Test STY zeropage."""
    write_memory(mpu._memory, 0x1000, (0x84, 0x10))  # 1000: STY $10
    write_memory(mpu._memory, 0x0010, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STY $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0010] == mpu.registers.Y
    assert mpu.elapsed_cycles == 3


def test_STY_zeropage_x(mpu: MPU):
    """Test STY zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x94, 0x10))  # 1000: STY $10,X
    write_memory(mpu._memory, 0x0013, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.Y = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STY $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0013] == mpu.registers.Y
    assert mpu.elapsed_cycles == 4


def test_STY_zeropage_x_with_overflow(mpu: MPU):
    """Test STY zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x94, 0xFF))  # 1000: STY $FF,X
    write_memory(mpu._memory, 0x0000, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.Y = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STY $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == mpu.registers.Y
    assert mpu.elapsed_cycles == 4


def test_STY_absolute(mpu: MPU):
    """Test STY absolute."""
    write_memory(mpu._memory, 0x1000, (0x8C, 0x00, 0x20))  # 1000: STY $2000
    write_memory(mpu._memory, 0x2000, (0x00, 0x00, 0x00))
    mpu.registers.Y = 0x1F
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: STY $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == mpu.registers.Y
    assert mpu.elapsed_cycles == 4
