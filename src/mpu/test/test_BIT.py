"""Test BIT operand."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using zeropage adressing mode ****
"""


def test_BIT_flags(mpu: MPU):
    """Test BIT operation, flags and result."""
    tests = [
        {
            "n": 0b0000_0000,
            "A": 0b0000_0000,
            "expectedFlags": "nv-bdicZ",
        },
        {
            "n": 0b1000_0000,
            "A": 0b0000_0001,
            "expectedFlags": "Nv-bdicZ",
        },
        {
            "n": 0b1100_0000,
            "A": 0b0000_0001,
            "expectedFlags": "NV-bdicZ",
        },
        {
            "n": 0b0000_1000,
            "A": 0b0000_1001,
            "expectedFlags": "nv-bdicz",
        },
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x24, 0x00))  # 1000: BIT $00
        write_memory(mpu._memory, 0x0000, (test["n"], 0x00))
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["A"]
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"A={format(test['A'], '#x')}"
            + f"= {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["A"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** BIT adressing modes ****
"""


def test_BIT_zeropage(mpu: MPU):
    """Test BIT zeropage."""
    write_memory(mpu._memory, 0x1000, (0x24, 0x10))  # BIT $10
    write_memory(mpu._memory, 0x0010, (0b1100_0000, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    mpu.registers.A = 0b0000_0001
    assert str(mpu.decode(0x1000)) == "1000: BIT $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0b0000_0001
    assert mpu._memory[0x0010] == 0b1100_0000
    assert mpu.registers.flags2str() == "NV-bdicZ"
    assert mpu.elapsed_cycles == 3


def test_BIT_absolute(mpu: MPU):
    """Test BIT absolute."""
    write_memory(mpu._memory, 0x1000, (0x2C, 0x00, 0x20))  # BIT $2000
    write_memory(mpu._memory, 0x2000, (0b1100_0000, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0
    mpu.registers.A = 0b0000_0001
    assert str(mpu.decode(0x1000)) == "1000: BIT $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0b0000_0001
    assert mpu._memory[0x2000] == 0b1100_0000
    assert mpu.registers.flags2str() == "NV-bdicZ"
    assert mpu.elapsed_cycles == 4
