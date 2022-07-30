"""Test stack initialization and operation."""
from fixtures import *  # noqa
from utils import write_memory
from mpu.mpu6502 import MPU


def test_stack_init(mpu: MPU):
    """Test stack initialization."""
    assert mpu.registers.SP == 0xFF, "Stack initialization error."


def test_stack_push(mpu: MPU):
    """Test stack push and growth."""
    mpu._push(0x56)
    assert mpu.registers.SP == 0xFE, "Stack does not grow down."
    assert mpu._memory[0x01FF] == 0x56, "Value not stored on stack."


def test_stack_push_word(mpu: MPU):
    """Test stack push word."""
    word = 0x1234
    mpu._push_word(word)
    assert mpu.registers.SP == 0xFD, "Stack not changed by 2 bytes."
    assert mpu._memory[0x01FF] == 0x12
    assert mpu._memory[0x01FE] == 0x34


def test_stack_push_pop(mpu: MPU):
    """Test stack push and pop."""
    value = None
    mpu._push(0x56)
    value = mpu._pop()
    assert value == 0x56
    assert mpu.registers.SP == 0xFF


def test_stack_push_pop_word(mpu: MPU):
    """Test stack push pop word."""
    value = None
    word = 0x1234
    mpu._push_word(word)
    value = mpu._pop_word()
    assert value == word, "Word push/pop not working."


def test_stack_overflow(mpu: MPU):
    """Test stack overflow."""
    for x in range(0xFF + 1):
        mpu._push(x)
    assert mpu.registers.SP == 0xFF, "SP doesn't do overflow."
    for x in range(0xFF + 1):
        assert mpu._memory[0x0100 + x] == 0xFF - x, "Stack not aligned properly."


def test_TXS(mpu: MPU):
    """Test TXS."""
    write_memory(mpu._memory, 0x1000, (0x9A,))  # TXS
    mpu.registers.PC = 0x1000
    mpu.registers.SP = 0x19
    mpu.registers.X = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: TXS", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 2
    assert mpu.registers.SP == 0xFF


def test_TSX(mpu: MPU):
    """Test TSX."""
    write_memory(mpu._memory, 0x1000, (0xBA,))  # TSX
    mpu.registers.PC = 0x1000
    mpu.registers.SP = 0x19
    mpu.registers.X = 0xFF
    assert str(mpu.decode(0x1000)) == "1000: TSX", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 2
    assert mpu.registers.X == 0x19


def test_PHA(mpu: MPU):
    """Test PHA."""
    write_memory(mpu._memory, 0x1000, (0x48,))  # PHA
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0x19
    assert str(mpu.decode(0x1000)) == "1000: PHA", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 3
    assert mpu.registers.SP == 0xFE, "SP not moved."
    assert mpu._memory[0x01FF] == 0x19, "Value on stack error."


def test_PLA(mpu: MPU):
    """Test PLA."""
    write_memory(mpu._memory, 0x1000, (0x68,))  # PLA
    # Prepare stack
    write_memory(mpu._memory, 0x01FF, (0x19,))
    mpu.registers.PC = 0x1000
    mpu.registers.A = 0xFF
    mpu.registers.SP = 0xFE
    assert str(mpu.decode(0x1000)) == "1000: PLA", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 4
    assert mpu.registers.SP == 0xFF, "SP not moved."
    assert mpu.registers.A == 0x19


def test_PHP(mpu: MPU):
    """Test PHP."""
    write_memory(mpu._memory, 0x1000, (0x08,))  # PHP
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0x19
    assert str(mpu.decode(0x1000)) == "1000: PHP", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 3
    assert mpu.registers.SP == 0xFE, "SP not moved."
    assert mpu._memory[0x01FF] == 0x19, "Value on stack error."


def test_PLP(mpu: MPU):
    """Test PLP."""
    write_memory(mpu._memory, 0x1000, (0x28,))  # PLP
    # Prepare stack
    write_memory(mpu._memory, 0x01FF, (0x19,))
    mpu.registers.PC = 0x1000
    mpu.registers.FLAGS = 0xFF
    mpu.registers.SP = 0xFE
    assert str(mpu.decode(0x1000)) == "1000: PLP", "Disassembler error."
    mpu.step()
    assert mpu.elapsed_cycles == 4
    assert mpu.registers.SP == 0xFF, "SP not moved."
    assert mpu.registers.FLAGS == 0x19
