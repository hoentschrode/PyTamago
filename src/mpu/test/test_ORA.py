"""Test ORA instruction."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test affected flags, using immediate adressing mode ****
"""


def test_ORA_flags(mpu: MPU):
    """Test ORA, flags and results."""
    # Test calculations: n (in A) OR m
    tests = [
        {"n": 0xFF, "m": 0x11, "expectedFlags": "Nv-bdicz", "expectedA": 0xFF},
        {"n": 0x00, "m": 0x00, "expectedFlags": "nv-bdicZ", "expectedA": 0x00},
        {"n": 0x7F, "m": 0x80, "expectedFlags": "Nv-bdicz", "expectedA": 0xFF},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x09, test["m"]))  # 1000: ORA# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["n"]
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"or {format(test['m'],'#x')} "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** ORA adressing modes ****
"""


def test_ORA_immediate(mpu: MPU):
    """Test ORA immediate."""
    write_memory(mpu._memory, 0x1000, (0x09, 0x0F))  # ORA #$0F
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA #$0F", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 2


def test_ORA_zeropage(mpu: MPU):
    """Test ORA zeropage."""
    write_memory(mpu._memory, 0x1000, (0x05, 0x10))  # 1000: ORA $10
    write_memory(mpu._memory, 0x0010, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 3


def test_ORA_zeropage_x(mpu: MPU):
    """Test ORA zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x15, 0x10))  # 1000: ORA $10,X
    write_memory(mpu._memory, 0x0013, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4


def test_ORA_zeropage_x_with_overflow(mpu: MPU):
    """Test ORA zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x15, 0xFF))  # 1000: ORA $FF,X
    write_memory(mpu._memory, 0x0000, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4


def test_ORA_absolute(mpu: MPU):
    """Test ORA absolute."""
    write_memory(mpu._memory, 0x1000, (0x0D, 0x00, 0x20))  # 1000: ORA $2000
    write_memory(mpu._memory, 0x2000, (0x0F,))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4


def test_ORA_absolute_x(mpu: MPU):
    """Test ORA absolute X."""
    write_memory(mpu._memory, 0x1000, (0x1D, 0x00, 0x20))  # 1000: ORA $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4


def test_ORA_absolute_x_wrapping(mpu: MPU):
    """Test ORA absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0x1D, 0xFF, 0xFF))  # 1000: ORA $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_ORA_absolute_y(mpu: MPU):
    """Test ORA absolute Y."""
    write_memory(mpu._memory, 0x1000, (0x19, 0x00, 0x20))  # 1000: ORA $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4


def test_ORA_absolute_y_wrapping(mpu: MPU):
    """Test ORA absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0x19, 0xFF, 0xFF))  # 1000: ORA $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 4 + 1


def test_ORA_indirect_x(mpu: MPU):
    """Test ORA indirect X."""
    write_memory(mpu._memory, 0x1000, (0x01, 0x12))  # 1000: ORA ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 6


def test_ORA_indirect_x_wrapping(mpu: MPU):
    """Test ORA indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x01, 0xFE))  # 1000: ORA ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x0F, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 6


def test_ORA_indirect_y(mpu: MPU):
    """Test ORA indirect Y."""
    write_memory(mpu._memory, 0x1000, (0x11, 0x12))  # 1000: ORA ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 5


def test_ORA_indirect_y_wrapping(mpu: MPU):
    """Test ORA indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x11, 0xFF))  # 1000: ORA ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0x0F, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x4D
    assert str(mpu.decode(0x1000)) == "1000: ORA ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x4F
    assert mpu.elapsed_cycles == 5 + 1
