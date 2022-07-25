"""Test MPU flag behaviour."""
import pytest
from mpu.utils import Registers, Flag


@pytest.fixture
def registers() -> Registers:
    registers = Registers(A=0, X=0, Y=0, FLAGS=0, PC=0, SP=0)
    return registers


def test_flag_set_reset(registers: Registers):
    """Test various flag accessors."""
    assert registers.FLAGS == 0
    for flag in Flag:
        # Initially resetted
        value = getattr(registers, flag.name)
        assert value is False, f"Flag: {flag.name}"
        assert registers.FLAGS == 0

        registers.set_flag(flag)
        assert registers.FLAGS == flag.value
        value = getattr(registers, flag.name)
        assert value is True, f"Flag: {flag.name}"

        registers.reset_flag(flag)
        value = getattr(registers, flag.name)
        assert value is False, f"Flag: {flag.name}"

        registers.modify_flag(flag, True)
        assert registers.FLAGS == flag.value
        value = getattr(registers, flag.name)
        assert value is True, f"Flag: {flag.name}"

        registers.modify_flag(flag, False)
        assert registers.FLAGS == 0
        value = getattr(registers, flag.name)
        assert value is False, f"Flag: {flag.name}"


def test_modify_nz(registers: Registers):
    """Test NZ modification."""
    assert registers.FLAGS == 0
    registers.modify_nz_flags(0)
    assert registers.NEGATIVE is False
    assert registers.ZERO is True

    registers.modify_nz_flags(1)
    assert registers.NEGATIVE is False
    assert registers.ZERO is False

    registers.modify_nz_flags(0b1000_0000)
    assert registers.NEGATIVE is True
    assert registers.ZERO is False


def test_reset_flags(registers: Registers):
    """Test reset of multiple registers."""
    assert registers.FLAGS == 0
    registers.set_flag(Flag.CARRY)
    registers.set_flag(Flag.NEGATIVE)
    registers.set_flag(Flag.OVERFLOW)
    registers.reset_flags([Flag.CARRY, Flag.NEGATIVE])
    assert registers.FLAGS == Flag.OVERFLOW.value


def test_set_flags(registers: Registers):
    """Set set of multiple registers."""
    assert registers.FLAGS == 0
    registers.set_flags([Flag.CARRY, Flag.OVERFLOW])
    assert registers.FLAGS == Flag.CARRY.value | Flag.OVERFLOW.value
