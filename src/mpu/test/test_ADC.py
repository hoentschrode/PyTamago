"""Test ADC instruction in binary mode."""
from mpu.utils import Flag
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU

"""
**** Test binary/decimal mode, using immediate adressing mode ****
"""


def test_ADC_binary_mode(mpu: MPU):
    """Test ADC binary operation, flags and results."""
    # Test calculations: n,m: values to add, c:Carry preset
    tests = [
        # Overflow tests (https://www.righto.com/2012/12/the-6502-overflow-flag-explained.html)
        {"n": 0x50, "m": 0x10, "c": False, "expectedFlags": "nv-bdicz", "expectedA": 0x60},
        {"n": 0x50, "m": 0x50, "c": False, "expectedFlags": "NV-bdicz", "expectedA": 0xA0},
        {"n": 0x50, "m": 0x90, "c": False, "expectedFlags": "Nv-bdicz", "expectedA": 0xE0},
        {"n": 0x50, "m": 0xD0, "c": False, "expectedFlags": "nv-bdiCz", "expectedA": 0x20},
        {"n": 0xD0, "m": 0x10, "c": False, "expectedFlags": "Nv-bdicz", "expectedA": 0xE0},
        {"n": 0xD0, "m": 0x50, "c": False, "expectedFlags": "nv-bdiCz", "expectedA": 0x20},
        {"n": 0xD0, "m": 0x90, "c": False, "expectedFlags": "nV-bdiCz", "expectedA": 0x60},
        {"n": 0xD0, "m": 0xD0, "c": False, "expectedFlags": "Nv-bdiCz", "expectedA": 0xA0},
        # Presetted carry
        {"n": 0x10, "m": 0x20, "c": True, "expectedFlags": "nv-bdicz", "expectedA": 0x31},
        # 0xff-overflow
        {"n": 0xFF, "m": 0x01, "c": False, "expectedFlags": "nv-bdiCZ", "expectedA": 0x00},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x69, test["m"]))  # 1000: ADC# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        # Preload A
        mpu.registers.A = test["n"]
        mpu.registers.modify_flag(Flag.CARRY, test["c"])
        mpu.step()
        case_description = (
            f"Case: {format(test['n'],'#x')} "
            + f"+ {format(test['m'],'#x')} "
            + f"(C={1 if test['c'] else 0}) "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


def test_ADC_decimal_mode(mpu: MPU):
    """Test ADC decimal operation, flags and results."""
    # Test calculations: n,m: values to add, c:Carry preset
    tests = [
        # Preset carry and decimal half-overflow
        {"n": 0x79, "m": 0x00, "c": True, "expectedFlags": "NV-bDicz", "expectedA": 0x80},
        {"n": 0x6F, "m": 0x00, "c": True, "expectedFlags": "nv-bDicz", "expectedA": 0x76},
        {"n": 0x9C, "m": 0x9D, "c": False, "expectedFlags": "nV-bDiCz", "expectedA": 0x9F},
    ]
    for test in tests:
        # Setup test
        write_memory(mpu._memory, 0x1000, (0x69, test["m"]))  # 1000: ADC# m
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        mpu.registers.set_flag(Flag.DECIMAL)
        # Preload A
        mpu.registers.A = test["n"]
        mpu.registers.modify_flag(Flag.CARRY, test["c"])
        mpu.step()
        case_description = (
            f"Case Decimal-Mode: {format(test['n'],'#x')} "
            + f"+ {format(test['m'],'#x')} "
            + f"(C={1 if test['c'] else 0}) "
            + f"= {format(test['expectedA'],'#x')}, {test['expectedFlags']}"
        )
        assert mpu.registers.A == test["expectedA"], case_description
        assert mpu.registers.flags2str() == test["expectedFlags"], case_description


"""
**** ADC adressing modes ****
"""


def test_ADC_immediate(mpu: MPU):
    """Test ADC immediate."""
    write_memory(mpu._memory, 0x1000, (0x69, 0x12))  # ADC #$12
    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC #$12", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 2


def test_ADC_zeropage(mpu: MPU):
    """Test ADC zeropage."""
    write_memory(mpu._memory, 0x1000, (0x65, 0x10))  # 1000: ADC $10
    write_memory(mpu._memory, 0x0010, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC $10", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 3


def test_ADC_zeropage_x(mpu: MPU):
    """Test ADC zeropage X."""
    write_memory(mpu._memory, 0x1000, (0x75, 0x10))  # 1000: ADC $10,X
    write_memory(mpu._memory, 0x0013, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x03
    assert str(mpu.decode(0x1000)) == "1000: ADC $10,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_ADC_zeropage_x_with_overflow(mpu: MPU):
    """Test ADC zeropage X overflow."""
    write_memory(mpu._memory, 0x1000, (0x75, 0xFF))  # 1000: ADC $FF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 0x01
    assert str(mpu.decode(0x1000)) == "1000: ADC $FF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_ADC_absolute(mpu: MPU):
    """Test ADC absolute."""
    write_memory(mpu._memory, 0x1000, (0x6D, 0x00, 0x20))  # 1000: ADC $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x00, 0x00))

    mpu.registers.PC = 0x1000
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC $2000", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4


def test_ADC_absolute_x(mpu: MPU):
    """Test ADC absolute X."""
    write_memory(mpu._memory, 0x1000, (0x7D, 0x00, 0x20))  # 1000: ADC $2000,X
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert mpu.registers.A == 0x00
    assert str(mpu.decode(0x1000)) == "1000: ADC $2000,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 4


def test_ADC_absolute_x_wrapping(mpu: MPU):
    """Test ADC absolute X full wrapping."""
    write_memory(mpu._memory, 0x1000, (0x7D, 0xFF, 0xFF))  # 1000: ADC $FFFF,X
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC $FFFF,X", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4 + 1, "One extra cycle needed for page boundary crossing."


def test_ADC_absolute_y(mpu: MPU):
    """Test ADC absolute Y."""
    write_memory(mpu._memory, 0x1000, (0x79, 0x00, 0x20))  # 1000: ADC $2000,Y
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC $2000,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 4


def test_ADC_absolute_y_wrapping(mpu: MPU):
    """Test ADC absolute Y wrapping."""
    write_memory(mpu._memory, 0x1000, (0x79, 0xFF, 0xFF))  # 1000: ADC $FFFF,Y
    write_memory(mpu._memory, 0x0000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC $FFFF,Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1003
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 4 + 1


def test_ADC_indirect_x(mpu: MPU):
    """Test ADC indirect X."""
    write_memory(mpu._memory, 0x1000, (0x61, 0x12))  # 1000: ADC ($12,X)
    write_memory(mpu._memory, 0x0013, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC ($12,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 6


def test_ADC_indirect_x_wrapping(mpu: MPU):
    """Test ADC indirect X with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x61, 0xFE))  # 1000: ADC ($FE,X)
    write_memory(mpu._memory, 0x00FF, (0x00, 0x00))  # 00ff: byte 00
    write_memory(mpu._memory, 0x0000, (0x20, 0x00))  # 0000: byte 20
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.X = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC ($FE,X)", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x12
    assert mpu.elapsed_cycles == 6


def test_ADC_indirect_y(mpu: MPU):
    """Test ADC indirect Y."""
    write_memory(mpu._memory, 0x1000, (0x71, 0x12))  # 1000: ADC ($12),Y
    write_memory(mpu._memory, 0x0012, (0x00, 0x20))  # 0012: byte $2000
    write_memory(mpu._memory, 0x2000, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC ($12),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 5


def test_ADC_indirect_y_wrapping(mpu: MPU):
    """Test ADC indirect Y with wrapping."""
    write_memory(mpu._memory, 0x1000, (0x71, 0xFF))  # 1000: ADC ($FF),Y
    write_memory(mpu._memory, 0x00FF, (0xFF,))  # 00ff: byte FF
    write_memory(mpu._memory, 0x0000, (0x20,))  # 0000: byte 20
    write_memory(mpu._memory, 0x20FF, (0x12, 0x34, 0x56))

    mpu.registers.PC = 0x1000
    mpu.registers.Y = 1
    assert mpu.registers.A == 0
    assert str(mpu.decode(0x1000)) == "1000: ADC ($FF),Y", "Disassembler error."
    mpu.step()
    assert mpu.registers.PC == 0x1002
    assert mpu.registers.A == 0x34
    assert mpu.elapsed_cycles == 5 + 1
