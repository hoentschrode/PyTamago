"""Test BRK instruction."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_BRK(mpu: MPU):
    """Test BRK."""
    # Set BRK vector
    write_memory(mpu._memory, MPU.MEM_VECTOR_IRQ_BRK, (0x00, 0x20))
    write_memory(mpu._memory, 0x1000, (0x00, 0x00))  # 1000: BRK
    mpu.registers.PC = 0x1000
    # Set decimal and carry flag just to check for something <> 0
    mpu.registers.set_flags([Flag.CARRY, Flag.DECIMAL])
    assert str(mpu.decode(0x1000)) == "1000: BRK", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x2000, "PC not pointing to BRK vector address."
    assert mpu.registers.INTERRUPT, "I flag not set."
    assert mpu.registers.BREAK, "B flag not set."
    # Analyse stack
    assert mpu.registers.SP == 0xFC, "Stack not grown by 3 byte."
    assert mpu._memory[0x01FF] == 0x10, "Return address HSB not on stack."
    assert mpu._memory[0x01FE] == 0x02, "Return address LSB not on stack."
    assert (
        mpu._memory[0x01FD] == Flag.CARRY.value | Flag.DECIMAL.value | Flag.BREAK.value
    ), "Flags not stored on stack."
