"""Test RTS instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_RTS(mpu: MPU):
    """Test RTS."""
    # Prepare stack
    write_memory(mpu._memory, 0x01FE, (0x05, 0x10))  # Return address - 1
    write_memory(mpu._memory, 0x1000, (0x60,))  # 1000: RTS
    mpu.registers.PC = 0x1000
    mpu.registers.SP = 0xFD
    assert str(mpu.decode(0x1000)) == "1000: RTS", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1005 + 1, "PC not pointing to RTS address from stack."
    # Analyse stack
    assert mpu.registers.SP == 0xFF, "Stack not shrunk."
