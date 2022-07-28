"""Test NOP instruction."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_NOP(mpu: MPU):
    """Test NOP."""
    write_memory(mpu._memory, 0x1000, (0xEA,))  # 1000: NOP
    mpu.registers.PC = 0x1000
    # Set decimal and carry flag just to check for something <> 0
    mpu.registers.set_flags([Flag.CARRY, Flag.DECIMAL])
    assert str(mpu.decode(0x1000)) == "1000: NOP", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1001
    assert mpu.registers.flags2str() == "nv-bDiCz"
