"""Test SBC instruction."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test binary/decimal mode, using immediate adressing mode ****
"""


def test_SBC_binary_mode(mpu: MPU):
    """Test SBC binary operation, flags and results."""
    # Test calculations: n,m: values to add, c:Carry preset
    tests = [
        # Overflow tests (https://www.righto.com/2012/12/the-6502-overflow-flag-explained.html)
        {"n": 0x50, "m": 0xF0, "c": False, "expectedFlags": "nv-bdicz", "expectedA": 0x60},
        {"n": 0x50, "m": 0xB0, "c": False, "expectedFlags": "NV-bdicz", "expectedA": 0xA0},
        {"n": 0x50, "m": 0x70, "c": False, "expectedFlags": "Nv-bdicz", "expectedA": 0xE0},
        {"n": 0x50, "m": 0x30, "c": False, "expectedFlags": "nv-bdiCz", "expectedA": 0x20},
        {"n": 0xD0, "m": 0xF0, "c": False, "expectedFlags": "Nv-bdicz", "expectedA": 0xE0},
        {"n": 0xD0, "m": 0xB0, "c": False, "expectedFlags": "nv-bdiCz", "expectedA": 0x20},
        {"n": 0xD0, "m": 0x70, "c": False, "expectedFlags": "nV-bdiCz", "expectedA": 0x60},
        {"n": 0xD0, "m": 0x30, "c": False, "expectedFlags": "Nv-bdiCz", "expectedA": 0xA0},
        # Preset carry
        {"n": 0xD0, "m": 0x30, "c": True, "expectedFlags": "Nv-bdiCz", "expectedA": 0xA1},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0xE9, test["m"]))  # 1000: SBC# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["n"]
        mpu.registers.modify_flag(Flag.CARRY, test["c"])
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"- {format(test['m'],'#x')} "
            + f"(C={1 if test['c'] else 0}) "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


def test_SDC_decimal_mode(mpu: MPU):
    """Test SDC decimal operation, flags and results."""
    # Test calculations: n (A) - m: c:Carry preset
    tests = [
        {"n": 0x79, "m": 0x00, "c": False, "expectedFlags": "nv-bDicz", "expectedA": 0x79},
        {"n": 0x79, "m": 0x00, "c": True, "expectedFlags": "nv-bDicz", "expectedA": 0x7A},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0xE9, test["m"]))  # 1000: DBC# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        mpu.registers.set_flag(Flag.DECIMAL)
        # Preload A
        mpu.registers.A = test["n"]
        mpu.registers.modify_flag(Flag.CARRY, test["c"])
        mpu.step()
        case_description = (
            f"Case Decimal-Mode: {format(test['n'],'#x')} "
            + f"- {format(test['m'],'#x')} "
            + f"(C={1 if test['c'] else 0}) "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** SDC adressing modes ****
"""


def test_SBC_immediate(mpu: MPU):
    """Test SBC immediate."""
    write_memory(mpu._memory, 0x1000, (0xE9, 0xF0))  # SDC #$F0
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0x00
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC #$F0", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 2


def test_SBC_zeropage(mpu: MPU):
    """Test SBC zeropage."""
    write_memory(mpu._memory, 0x1000, (0xE5, 0x10))  # 1000: DBC $10
    write_memory(mpu._memory, 0x0010, (0xF0, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 3


def test_SBC_zeropage_x(mpu: MPU):
    """Test SBC zeropage X."""
    write_memory(mpu._memory, 0x1000, (0xF5, 0x10))  # 1000: SBC $10,X
    write_memory(mpu._memory, 0x0013, (0xF0, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4


def test_SBC_zeropage_x_with_overflow(mpu: MPU):
    """Test SBC zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0xF5, 0xFF))  # 1000: SBC $FF,X
    write_memory(mpu._memory, 0x0000, (0xF0, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4


def test_SBC_absolute(mpu: MPU):
    """Test SBC absolute."""
    write_memory(mpu._memory, 0x1000, (0xED, 0x00, 0x20))  # 1000: SBC $2000
    write_memory(mpu._memory, 0x2000, (0xF0, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4


def test_SBC_absolute_x(mpu: MPU):
    """Test SBC absolute X."""
    write_memory(mpu._memory, 0x1000, (0xFD, 0x00, 0x20))  # 1000: SBC $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0xF0, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4


def test_SBC_absolute_x_wrapping(mpu: MPU):
    """Test SBC absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0xFD, 0xFF, 0xFF))  # 1000: SBC $FFFF,X
    write_memory(mpu._memory, 0x0000, (0xF0, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_SBC_absolute_y(mpu: MPU):
    """Test SBC absolute Y."""
    write_memory(mpu._memory, 0x1000, (0xF9, 0x00, 0x20))  # 1000: SBC $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0xF0, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4


def test_SBC_absolute_y_wrapping(mpu: MPU):
    """Test SBC absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0xF9, 0xFF, 0xFF))  # 1000: SBC $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0xF0, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 4 + 1


def test_SBC_indirect_x(mpu: MPU):
    """Test SBC indirect X."""
    write_memory(mpu._memory, 0x1000, (0xE1, 0x12))  # 1000: SBC ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0xF0, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 6


def test_SBC_indirect_x_wrapping(mpu: MPU):
    """Test SBC indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xE1, 0xFE))  # 1000: SBC ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0xF0, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 6


def test_SBC_indirect_y(mpu: MPU):
    """Test SBC indirect Y."""
    write_memory(mpu._memory, 0x1000, (0xF1, 0x12))  # 1000: SBC ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0xF0, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 5


def test_SBC_indirect_y_wrapping(mpu: MPU):
    """Test SBC indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0xF1, 0xFF))  # 1000: SBC ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0xF0, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    mpu.registers.A = 0x50
    assert str(mpu.decode(0x1000)) == "1000: SBC ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x60
    assert mpu.elapsed_cycles == 5 + 1
