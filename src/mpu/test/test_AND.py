"""Test AND instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using immediate adressing mode ****
"""


def test_AND_flags(mpu: MPU):
    """Test AND, flags and results."""
    # Test calculations: n AND m
    tests = [
        {"n": 0xFF, "m": 0x11, "expectedFlags": "nv-bdicz", "expectedA": 0x11},
        {"n": 0x20, "m": 0x00, "expectedFlags": "nv-bdicZ", "expectedA": 0x00},
        {"n": 0xFF, "m": 0xFE, "expectedFlags": "Nv-bdicz", "expectedA": 0xFE},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x29, test["m"]))  # 1000: AND# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["n"]
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"+ {format(test['m'],'#x')} "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** AND adressing modes ****
"""


def test_AND_immediate(mpu: MPU):
    """Test AND immediate."""
    write_memory(mpu._memory, 0x1000, (0x29, 0x0F))  # AND #$0F
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND #$0F", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 2


def test_AND_zeropage(mpu: MPU):
    """Test AND zeropage."""
    write_memory(mpu._memory, 0x1000, (0x25, 0x10))  # 1000: AND $10
    write_memory(mpu._memory, 0x0010, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 3


def test_AND_zeropage_x(mpu: MPU):
    """Test AND zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x35, 0x10))  # 1000: AND $10,X
    write_memory(mpu._memory, 0x0013, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4


def test_AND_zeropage_x_with_overflow(mpu: MPU):
    """Test AND zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x35, 0xFF))  # 1000: AND $FF,X
    write_memory(mpu._memory, 0x0000, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4


def test_AND_absolute(mpu: MPU):
    """Test AND absolute."""
    write_memory(mpu._memory, 0x1000, (0x2D, 0x00, 0x20))  # 1000: AND $2000
    write_memory(mpu._memory, 0x2000, (0x0F, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4


def test_AND_absolute_x(mpu: MPU):
    """Test AND absolute X."""
    write_memory(mpu._memory, 0x1000, (0x3D, 0x00, 0x20))  # 1000: AND $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4


def test_AND_absolute_x_wrapping(mpu: MPU):
    """Test AND absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0x3D, 0xFF, 0xFF))  # 1000: AND $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_AND_absolute_y(mpu: MPU):
    """Test AND absolute Y."""
    write_memory(mpu._memory, 0x1000, (0x39, 0x00, 0x20))  # 1000: AND $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4


def test_AND_absolute_y_wrapping(mpu: MPU):
    """Test AND absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0x39, 0xFF, 0xFF))  # 1000: AND $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 4 + 1


def test_AND_indirect_x(mpu: MPU):
    """Test AND indirect X."""
    write_memory(mpu._memory, 0x1000, (0x21, 0x12))  # 1000: AND ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 6


def test_AND_indirect_x_wrapping(mpu: MPU):
    """Test AND indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x21, 0xFE))  # 1000: AND ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 6


def test_AND_indirect_y(mpu: MPU):
    """Test AND indirect Y."""
    write_memory(mpu._memory, 0x1000, (0x31, 0x12))  # 1000: AND ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 5


def test_AND_indirect_y_wrapping(mpu: MPU):
    """Test AND indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x31, 0xFF))  # 1000: AND ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: AND ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x0D
    assert mpu.elapsed_cycles == 5 + 1
