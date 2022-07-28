"""Test JSR instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_JSR(mpu: MPU):
    """Test JSR."""
    write_memory(mpu._memory, 0x1000, (0x20, 0x00, 0x20))  # 1000: JSR $2000
    mpu.registers.PC = 0x1000
    assert str(mpu.decode(0x1000)) == "1000: JSR $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x2000, "PC not pointing to JSR address."
    # Analyse stack
    assert mpu.registers.SP == 0xFD, "Stack not grown by 2 byte."
    assert mpu._memory[0x01FF] == 0x10, "Return address HSB not on stack."
    assert mpu._memory[0x01FE] == 0x02, "Return address LSB not on stack."
