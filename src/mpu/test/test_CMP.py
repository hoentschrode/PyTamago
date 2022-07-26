"""Test CMP instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test flag behaviour using immediate adressing mode ****
"""


def test_CMP_flags(mpu: MPU):
    """Test CMP and flags."""
    # A:Accumulator, n:Test value
    tests = [
        # A == n
        {"A": 0x10, "n": 0x10, "expectedFlags": "nv-bdiCZ"},
        # A > n
        {"A": 0x2F, "n": 0x10, "expectedFlags": "nv-bdiCz"},
        # A < n
        {"A": 0x10, "n": 0x2F, "expectedFlags": "Nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xC9, test["n"]))  # CMP #$n
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["A"]
        mpu.step()
        case_description = (
            f"A:{format(test['A'], '#x')}, "
            + f"n:{format(test['n'],'#x')} = {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["A"], f"{case_description}: A was modified."
        assert (
            mpu.registers.flags2str() == test["expectedFlags"]
        ), f"{case_description}: Flag mismatch."


"""
**** CMP adressing modes ****
"""


def test_CMP_immediate(mpu: MPU):
    """Test CMP immediate."""
    write_memory(mpu._memory, 0x1000, (0xC9, 0x34))  # CMP #$34
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CMP #$34", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 2


def test_CMP_zeropage(mpu: MPU):
    """Test CMP zeropage."""
    write_memory(mpu._memory, 0x1000, (0xC5, 0x10))  # CMP $10
    write_memory(mpu._memory, 0x0010, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CMP $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 3


def test_CMP_zeropage_x(mpu: MPU):
    """Test CMP zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xD5, 0x10))  # CMP $10,X
    write_memory(mpu._memory, 0x0010, (0x00, 0x34))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4


def test_CMP_zeropage_x_with_overflow(mpu: MPU):
    """Test CMP zeropage X with overflow."""
    write_memory(mpu._memory, 0x1000, (0xD5, 0xFF))  # CMP $FF,X
    write_memory(mpu._memory, 0x0000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4


def test_CMP_absolute(mpu: MPU):
    """Test CMP absolute."""
    write_memory(mpu._memory, 0x1000, (0xCD, 0x00, 0x20))  # CMP $2000
    write_memory(mpu._memory, 0x2000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    assert str(mpu.decode(0x1000)) == "1000: CMP $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4


def test_CMP_absolute_x(mpu: MPU):
    """Test CMP absolute X."""
    write_memory(mpu._memory, 0x1000, (0xDD, 0x00, 0x20))  # CMP $2000,X
    write_memory(mpu._memory, 0x2000, (0x00, 0x34))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4


def test_CMP_absolute_x_wrapping(mpu: MPU):
    """Test CMP absolute X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xDD, 0xFF, 0xFF))  # CMP $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 5


def test_CMP_absolute_y(mpu: MPU):
    """Test CMP absolute Y."""
    write_memory(mpu._memory, 0x1000, (0xD9, 0x00, 0x20))  # CMP $2000,Y
    write_memory(mpu._memory, 0x2000, (0x00, 0x34))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 4


def test_CMP_absolute_y_wrapping(mpu: MPU):
    """Test CMP absolute Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xD9, 0xFF, 0xFF))  # CMP $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 5


def test_CMP_indirect_x(mpu: MPU):
    """Test CMP indirect X."""
    write_memory(mpu._memory, 0x1000, (0xC1, 0x12))  # CMP ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))
    write_memory(mpu._memory, 0x2000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_CMP_indirect_x_wrapping(mpu: MPU):
    """Test CMP indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xC1, 0xFE))  # CMP ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))
    write_memory(mpu._memory, 0x2000, (0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.X = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 6


def test_CMP_indirect_y(mpu: MPU):
    """Test CMP indirect Y."""
    write_memory(mpu._memory, 0x1000, (0xD1, 0x12))  # CMP ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))
    write_memory(mpu._memory, 0x2000, (0x00, 0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 5


def test_CMP_indirect_y_wrapping(mpu: MPU):
    """Test CMP indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xD1, 0xFF))  # CMP ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))
    write_memory(mpu._memory, 0x0000, (0x20,))
    write_memory(mpu._memory, 0x20FF, (0x00, 0x34, 0x00))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x12
    mpu.registers.Y = 1
    assert str(mpu.decode(0x1000)) == "1000: CMP ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.registers.flags2str() == "Nv-bdicz"
    assert mpu.elapsed_cycles == 6
