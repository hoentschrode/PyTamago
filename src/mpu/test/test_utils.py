"""Test various utility functions."""
from mpu.utils import byte2bin, two_complement_to_dec, dec_to_two_complement


def test_byte2bin():
    """Test byte2bin."""
    assert byte2bin(0b1001_0110) == "10010110"


def test_two_complement_to_dec():
    """Test two_complement_to_dec."""
    assert two_complement_to_dec(0x00) == 0
    assert two_complement_to_dec(0x01) == 1
    assert two_complement_to_dec(0x7F) == 127
    assert two_complement_to_dec(0x80) == -128
    assert two_complement_to_dec(0xFF) == -1


def test_dec_to_two_complement():
    """Test dec_to_two_complement."""
    assert dec_to_two_complement(0) == 0x00
    assert dec_to_two_complement(1) == 0x01
    assert dec_to_two_complement(127) == 0x7F
    assert dec_to_two_complement(-128) == 0x80
    assert dec_to_two_complement(-1) == 0xFF
