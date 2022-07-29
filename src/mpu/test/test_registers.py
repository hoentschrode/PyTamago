"""Test MPU registers."""
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


def test_TAX(mpu: MPU):
    """Test TAX."""
    tests = [
        {"A": 0x00, "expectedFlags": "nv-bdicZ"},
        {"A": 0x80, "expectedFlags": "Nv-bdicz"},
        {"A": 0x0F, "expectedFlags": "nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xAA,))
        assert str(mpu.decode(0x1000)) == "1000: TAX", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.A = test["A"]
        mpu.registers.X = 0x01
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.X == test["A"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_TAY(mpu: MPU):
    """Test TAY."""
    tests = [
        {"A": 0x00, "expectedFlags": "nv-bdicZ"},
        {"A": 0x80, "expectedFlags": "Nv-bdicz"},
        {"A": 0x0F, "expectedFlags": "nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xA8,))
        assert str(mpu.decode(0x1000)) == "1000: TAY", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.A = test["A"]
        mpu.registers.Y = 0x01
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.Y == test["A"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_TXA(mpu: MPU):
    """Test TXA."""
    tests = [
        {"X": 0x00, "expectedFlags": "nv-bdicZ"},
        {"X": 0x80, "expectedFlags": "Nv-bdicz"},
        {"X": 0x0F, "expectedFlags": "nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0x8A,))
        assert str(mpu.decode(0x1000)) == "1000: TXA", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.X = test["X"]
        mpu.registers.A = 0x01
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.A == test["X"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_TYA(mpu: MPU):
    """Test TYA."""
    tests = [
        {"Y": 0x00, "expectedFlags": "nv-bdicZ"},
        {"Y": 0x80, "expectedFlags": "Nv-bdicz"},
        {"Y": 0x0F, "expectedFlags": "nv-bdicz"},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0x98,))
        assert str(mpu.decode(0x1000)) == "1000: TYA", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.Y = test["Y"]
        mpu.registers.A = 0x01
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.A == test["Y"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_DEX(mpu: MPU):
    """Test DEX."""
    tests = [
        {"X": 0x00, "expectedFlags": "Nv-bdicz", "expectedX": 0xFF},
        {"X": 0x01, "expectedFlags": "nv-bdicZ", "expectedX": 0x00},
        {"X": 0x02, "expectedFlags": "nv-bdicz", "expectedX": 0x01},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xCA,))
        assert str(mpu.decode(0x1000)) == "1000: DEX", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.X = test["X"]
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.X == test["expectedX"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_DEY(mpu: MPU):
    """Test DEY."""
    tests = [
        {"Y": 0x00, "expectedFlags": "Nv-bdicz", "expectedY": 0xFF},
        {"Y": 0x01, "expectedFlags": "nv-bdicZ", "expectedY": 0x00},
        {"Y": 0x02, "expectedFlags": "nv-bdicz", "expectedY": 0x01},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0x88,))
        assert str(mpu.decode(0x1000)) == "1000: DEY", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.Y = test["Y"]
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.Y == test["expectedY"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_INX(mpu: MPU):
    """Test INX."""
    tests = [
        {"X": 0x00, "expectedFlags": "nv-bdicz", "expectedX": 0x01},
        {"X": 0xFF, "expectedFlags": "nv-bdicZ", "expectedX": 0x00},
        {"X": 0x7F, "expectedFlags": "Nv-bdicz", "expectedX": 0x80},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xE8,))
        assert str(mpu.decode(0x1000)) == "1000: INX", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.X = test["X"]
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.X == test["expectedX"]
        assert mpu.registers.flags2str() == test["expectedFlags"]


def test_INY(mpu: MPU):
    """Test INY."""
    tests = [
        {"Y": 0x00, "expectedFlags": "nv-bdicz", "expectedY": 0x01},
        {"Y": 0xFF, "expectedFlags": "nv-bdicZ", "expectedY": 0x00},
        {"Y": 0x7F, "expectedFlags": "Nv-bdicz", "expectedY": 0x80},
    ]
    for test in tests:
        write_memory(mpu._memory, 0x1000, (0xC8,))
        assert str(mpu.decode(0x1000)) == "1000: INY", "Disassembler error."
        mpu.registers.PC = 0x1000
        mpu.registers.Y = test["Y"]
        mpu.registers.FLAGS = 0
        mpu.step()
        assert mpu.registers.Y == test["expectedY"]
        assert mpu.registers.flags2str() == test["expectedFlags"]
