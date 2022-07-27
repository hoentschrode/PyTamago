"""Test EOR instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using immediate adressing mode ****
"""


def test_EOR_flags(mpu: MPU):
    """Test EOR, flags and results."""
    # Test calculations: A EOR n
    tests = [
        {"A": 0b0110_1001, "n": 0b1111_0000, "expectedFlags": "Nv-bdicz", "expectedA": 0b1001_1001},
        {"A": 0b0110_1001, "n": 0b0110_1001, "expectedFlags": "nv-bdicZ", "expectedA": 0b0000_0000},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x49, test["n"]))  # 1000: EOR #n
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["A"]
        mpu.step()
        case_description = (
            f"Case: A:{format(test['A'],'#x')}, "
            + f"n {format(test['n'],'#x')} "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** EOR adressing modes ****
"""


def test_EOR_immediate(mpu: MPU):
    """Test EOR immediate."""
    write_memory(mpu._memory, 0x1000, (0x49, 0x0F))  # EOR #$0F
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR #$0F", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 2


def test_EOR_zeropage(mpu: MPU):
    """Test EOR zeropage."""
    write_memory(mpu._memory, 0x1000, (0x45, 0x10))  # 1000: EOR $10
    write_memory(mpu._memory, 0x0010, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 3


def test_EOR_zeropage_x(mpu: MPU):
    """Test EOR zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x55, 0x10))  # 1000: EOR $10,X
    write_memory(mpu._memory, 0x0010, (0x00, 0x0F))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4


def test_EOR_zeropage_x_with_overflow(mpu: MPU):
    """Test EOR zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x55, 0xFF))  # 1000: EOR $FF,X
    write_memory(mpu._memory, 0x0000, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4


def test_EOR_absolute(mpu: MPU):
    """Test EOR absolute."""
    write_memory(mpu._memory, 0x1000, (0x4D, 0x00, 0x20))  # 1000: EOR $2000
    write_memory(mpu._memory, 0x2000, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4


def test_EOR_absolute_x(mpu: MPU):
    """Test EOR absolute X."""
    write_memory(mpu._memory, 0x1000, (0x5D, 0x00, 0x20))  # 1000: EOR $2000,X
    write_memory(mpu._memory, 0x2000, (0x00, 0x0F, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4


def test_EOR_absolute_x_wrapping(mpu: MPU):
    """Test EOR absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0x5D, 0xFF, 0xFF))  # 1000: EOR $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_EOR_absolute_y(mpu: MPU):
    """Test EOR absolute Y."""
    write_memory(mpu._memory, 0x1000, (0x59, 0x00, 0x20))  # 1000: EOR $2000,Y
    write_memory(mpu._memory, 0x2000, (0x00, 0x0F, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4


def test_EOR_absolute_y_wrapping(mpu: MPU):
    """Test EOR absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0x59, 0xFF, 0xFF))  # 1000: EOR $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 4 + 1


def test_EOR_indirect_x(mpu: MPU):
    """Test EOR indirect X."""
    write_memory(mpu._memory, 0x1000, (0x41, 0x12))  # 1000: EOR ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 6


def test_EOR_indirect_x_wrapping(mpu: MPU):
    """Test EOR indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x41, 0xFE))  # 1000: EOR ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 6


def test_EOR_indirect_y(mpu: MPU):
    """Test EOR indirect Y."""
    write_memory(mpu._memory, 0x1000, (0x51, 0x12))  # 1000: EOR ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x00, 0x0F))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 5


def test_EOR_indirect_y_wrapping(mpu: MPU):
    """Test EOR indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x51, 0xFF))  # 1000: EOR ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x00, 0x0F))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: EOR ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0xF0
    assert mpu.elapsed_cycles == 5 + 1
