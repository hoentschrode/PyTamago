"""Test STX instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_STX_zeropage(mpu: MPU):
    """Test STX zeropage."""
    write_memory(mpu._memory, 0x1000, (0x86, 0x10))  # 1000: STX $10
    write_memory(mpu._memory, 0x0010, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STX $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0010] == mpu.registers.X
    assert mpu.elapsed_cycles == 3


def test_STX_zeropage_y(mpu: MPU):
    """Test STX zeropage Y."""
    write_memory(mpu._memory, 0x1000, (0x96, 0x10))  # 1000: STX $10,Y
    write_memory(mpu._memory, 0x0013, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x03
    mpu.registers.X = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STX $10,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0013] == mpu.registers.X
    assert mpu.elapsed_cycles == 4


def test_STX_zeropage_y_with_overflow(mpu: MPU):
    """Test STX zeropage Y overflow."""
    write_memory(mpu._memory, 0x1000, (0x96, 0xFF))  # 1000: STX $FF,Y
    write_memory(mpu._memory, 0x0000, (0x00, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 0x01
    mpu.registers.X = 0x1F
    assert str(mpu.decode(0x1000)) == "1000: STX $FF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu._memory[0x0000] == mpu.registers.X
    assert mpu.elapsed_cycles == 4


def test_STX_absolute(mpu: MPU):
    """Test STX absolute."""
    write_memory(mpu._memory, 0x1000, (0x8E, 0x00, 0x20))  # 1000: STX $2000
    write_memory(mpu._memory, 0x2000, (0x00, 0x00, 0x00))
    mpu.registers.X = 0x1F
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: STX $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu._memory[0x2000] == mpu.registers.X
    assert mpu.elapsed_cycles == 4
