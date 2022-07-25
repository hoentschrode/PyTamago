"""Test conditional branches operand."""
import pytest
from mpu.utils import Flag, dec_to_two_complement
from utils import write_memory
from fixtures import *  # noqa
from mpu.mpu6502 import MPU


@pytest.fixture
def branches_not_taken():
    """Definition and setup for all branches not to be taken."""
    return [
        {"opcode": 0x10, "mnemonic": "BPL", "flag": Flag.NEGATIVE, "flagValue": True},
        {"opcode": 0x30, "mnemonic": "BMI", "flag": Flag.NEGATIVE, "flagValue": False},
        {"opcode": 0x50, "mnemonic": "BVC", "flag": Flag.OVERFLOW, "flagValue": True},
        {"opcode": 0x70, "mnemonic": "BVS", "flag": Flag.OVERFLOW, "flagValue": False},
        {"opcode": 0x90, "mnemonic": "BCC", "flag": Flag.CARRY, "flagValue": True},
        {"opcode": 0xB0, "mnemonic": "BCS", "flag": Flag.CARRY, "flagValue": False},
        {"opcode": 0xD0, "mnemonic": "BNE", "flag": Flag.ZERO, "flagValue": True},
        {"opcode": 0xF0, "mnemonic": "BEQ", "flag": Flag.ZERO, "flagValue": False},
    ]


@pytest.fixture
def branches_taken():
    """Definition and setup for all branchaes to be taken."""
    return [
        {"opcode": 0x10, "mnemonic": "BPL", "flag": Flag.NEGATIVE, "flagValue": False},
        {"opcode": 0x30, "mnemonic": "BMI", "flag": Flag.NEGATIVE, "flagValue": True},
        {"opcode": 0x50, "mnemonic": "BVC", "flag": Flag.OVERFLOW, "flagValue": False},
        {"opcode": 0x70, "mnemonic": "BVS", "flag": Flag.OVERFLOW, "flagValue": True},
        {"opcode": 0x90, "mnemonic": "BCC", "flag": Flag.CARRY, "flagValue": False},
        {"opcode": 0xB0, "mnemonic": "BCS", "flag": Flag.CARRY, "flagValue": True},
        {"opcode": 0xD0, "mnemonic": "BNE", "flag": Flag.ZERO, "flagValue": False},
        {"opcode": 0xF0, "mnemonic": "BEQ", "flag": Flag.ZERO, "flagValue": True},
    ]


def test_branch_not_taken(mpu: MPU, branches_not_taken):
    """Test all branches, not taken."""
    cycle_count = 0
    for test in branches_not_taken:
        write_memory(mpu._memory, 0x1000, (test["opcode"], 0x12))
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x1000)) == f"1000: {test['mnemonic']} $12", "Disassembler error"
        mpu.step()
        assert mpu.registers.PC == 0x1002, f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 2, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_forward(mpu: MPU, branches_taken):
    """Test all branches, taken forward."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0x1000, (test["opcode"], 0x12))
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x1000)) == f"1000: {test['mnemonic']} $12", "Disassembler error"
        mpu.step()
        assert mpu.registers.PC == 0x1000 + 2 + 0x12, f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 3, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_forward_with_overflow(mpu: MPU, branches_taken):
    """Test all branches, taken forward with page overflow."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0x10FE, (test["opcode"], 0x12))
        mpu.registers.PC = 0x10FE
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x10FE)) == f"10FE: {test['mnemonic']} $12", "Disassembler error"
        mpu.step()
        assert mpu.registers.PC == 0x10FE + 2 + 0x12, f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 4, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_forward_with_wrapping(mpu: MPU, branches_taken):
    """Test all branches, taken forward with page overflow and wrapping."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0xFFFE, (test["opcode"], 0x12))
        mpu.registers.PC = 0xFFFE
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0xFFFE)) == f"FFFE: {test['mnemonic']} $12", "Disassembler error"
        mpu.step()
        assert (
            mpu.registers.PC == ((0xFFFE + 2) & 0xFFFF) + 0x12
        ), f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 4, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_backwards(mpu: MPU, branches_taken):
    """Test all branches, taken backwards."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0x11F0, (test["opcode"], dec_to_two_complement(-5)))
        mpu.registers.PC = 0x11F0
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x11F0)) == f"11F0: {test['mnemonic']} -$05", "Disassembler error"
        mpu.step()
        assert mpu.registers.PC == 0x11F0 + 2 - 5, f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 3, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_backwards_with_overflow(mpu: MPU, branches_taken):
    """Test all branches, taken backwards with page overflow."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0x1000, (test["opcode"], dec_to_two_complement(-5)))
        mpu.registers.PC = 0x1000
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x1000)) == f"1000: {test['mnemonic']} -$05", "Disassembler error"
        mpu.step()
        assert mpu.registers.PC == 0x1000 + 2 - 5, f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 4, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles


def test_branch_taken_backwards_with_wrapping(mpu: MPU, branches_taken):
    """Test all branches, taken backwards with page overflow."""
    cycle_count = 0
    for test in branches_taken:
        write_memory(mpu._memory, 0x0000, (test["opcode"], dec_to_two_complement(-5)))
        mpu.registers.PC = 0x0000
        mpu.registers.FLAGS = 0
        mpu.registers.modify_flag(test["flag"], test["flagValue"])
        assert str(mpu.decode(0x0000)) == f"0000: {test['mnemonic']} -$05", "Disassembler error"
        mpu.step()
        assert (
            mpu.registers.PC == (0x0000 + 2 - 5) & 0xFFFF
        ), f"Instruction {test['mnemonic']} failed."
        assert mpu.elapsed_cycles - cycle_count == 4, f"Instruction {test['mnemonic']} failed."
        cycle_count = mpu.elapsed_cycles
