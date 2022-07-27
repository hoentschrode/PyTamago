"""Test JMP instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_JMP_absolute(mpu: MPU):
    """Test JMP absolute."""
    write_memory(mpu._memory, 0x1000, (0x4C, 0x00, 0x20))  # 1000: JMP $2000
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: JMP $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x2000, "PC not pointing to JMP destionation address."


def test_JMP_indirect(mpu: MPU):
    """Test JMP indirect."""
    write_memory(mpu._memory, 0x1000, (0x6C, 0x00, 0x20))  # 1000: JMP ($2000)
    write_memory(mpu._memory, 0x2000, (0x00, 0x30))  # jump vector
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: JMP ($2000)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x3000, "PC not pointing to JMP destionation address."


def test_JMP_indirect_with_page_wrapping(mpu: MPU):
    """Test JMP indirect."""
    write_memory(mpu._memory, 0x1000, (0x6C, 0xFF, 0x20))  # 1000: JMP ($20FF)
    write_memory(mpu._memory, 0x20FF, (0x00, 0xFF))  # jump vector lsb
    write_memory(mpu._memory, 0x2000, (0x40,))  # jump vector msb
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: JMP ($20FF)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x4000, "PC not pointing to JMP destionation address."
