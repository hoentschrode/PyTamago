"""Test stack initialization and operation."""
from fixtures import *  # noqa
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
