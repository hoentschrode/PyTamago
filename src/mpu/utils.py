"""Utility objects."""
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum, auto


class AddressMode(Enum):
    """Adressing modes."""

    NONE = auto()
    BRANCH = auto()
    ACCUMULATOR = auto()
    IMPLIED = auto()
    IMMEDIATE = auto()
    ZEROPAGE = auto()
    ZEROPAGE_X = auto()
    ABSOLUTE = auto()
    ABSOLUTE_X = auto()
    ABSOLUTE_Y = auto()
    INDIRECT_X = auto()
    INDIRECT_Y = auto()


@dataclass
class Instruction:
    """Define a single instruction."""

    opcode: int
    cycles: int
    bytes: int
    mnemonic: str
    address_mode: AddressMode
    exec: None


@dataclass
class DecodedInstruction(Instruction):
    """Same as instruction but with decoded operand and address."""

    operand: Optional[int] = None
    address: Optional[int] = None
    extra_cycles: int = 0

    def _format_operand(self) -> str:
        """Format the operand according to address mode."""
        if self.address_mode == AddressMode.BRANCH:
            displacement = two_complement_to_dec(self.operand)
            if displacement >= 0:
                return f" ${displacement:02X}"
            return f" -${-displacement:02X}"
        elif self.address_mode == AddressMode.ACCUMULATOR:
            return " A"
        elif self.address_mode == AddressMode.IMMEDIATE:
            return f" #${self.operand:02X}"
        elif self.address_mode == AddressMode.ZEROPAGE:
            return f" ${self.operand:02X}"
        elif self.address_mode == AddressMode.ZEROPAGE_X:
            return f" ${self.operand:02X},X"
        elif self.address_mode == AddressMode.ABSOLUTE:
            return f" ${self.operand:04X}"
        elif self.address_mode == AddressMode.ABSOLUTE_X:
            return f" ${self.operand:04X},X"
        elif self.address_mode == AddressMode.ABSOLUTE_Y:
            return f" ${self.operand:04X},Y"
        elif self.address_mode == AddressMode.INDIRECT_X:
            return f" (${self.operand:02X},X)"
        elif self.address_mode == AddressMode.INDIRECT_Y:
            return f" (${self.operand:02X}),Y"
        elif self.address_mode == AddressMode.IMPLIED:
            return ""

        raise NotImplementedError(f"Address mode f{self.address_mode.name} not implemented.")

    def print(self, include_opcodes=False) -> str:
        """Disassemble instruction and pretty print."""
        sfmt = "{address:04X}:{opcodes}{mnemonic}"

        opcodes = ""
        if include_opcodes:
            opcodes = f" {self.opcode:02X}"
            if self.bytes == 2:
                opcodes += f" {self.operand:02X}"
            elif self.bytes == 3:
                high = self.operand >> 8
                low = self.operand & 0x00FF
                opcodes += f" {low:02X} {high:02X}"
            # Ensure opcode block is 9 characters width (3 bytes max. + spaces)
            opcodes = f"{opcodes: <9}"

        mnem = f" {self.mnemonic}" + self._format_operand()

        return sfmt.format(address=self.address, opcodes=opcodes, mnemonic=mnem)

    def __repr__(self):
        """Return string representation."""
        return self.print()


class Flag(Enum):
    """Processor flag names and bitmasks."""

    NEGATIVE = 0b1000_0000
    OVERFLOW = 0b0100_0000
    UNUSED = 0x0010_0000
    BREAK = 0b0001_0000
    DECIMAL = 0b0000_1000
    INTERRUPT = 0b0000_0100
    ZERO = 0b0000_0010
    CARRY = 0b0000_0001


@dataclass
class Registers:
    """MPU registers incl. flags."""

    A: int
    X: int
    Y: int
    FLAGS: int
    PC: int
    SP: int

    def set_flag(self, flag: Flag):
        """Set a flag."""
        self.FLAGS |= flag.value

    def set_flags(self, flags: List[Flag]):
        """Set multiple flags."""

        def f(x: Flag):
            return x.value

        value = sum(map(lambda x: f(x), flags))
        self.FLAGS |= value

    def reset_flag(self, flag: Flag):
        """Reset a flag."""
        self.FLAGS &= ~flag.value

    def reset_flags(self, flags: List[Flag]):
        """Reset multiple flags."""

        def f(x: Flag):
            return x.value

        value = sum(map(lambda x: f(x), flags))
        self.FLAGS &= ~value

    def modify_flag(self, flag: Flag, condition):
        """Set or reset flag according to condition."""
        if condition:
            self.set_flag(flag)
        else:
            self.reset_flag(flag)

    def modify_nz_flags(self, value: int):
        """Set ZERO and NEGATIVE flag according to value."""
        self.modify_flag(Flag.ZERO, (value & 0xFF) == 0)
        self.modify_flag(Flag.NEGATIVE, (value & 0xFF) & Flag.NEGATIVE.value)

    @property
    def NEGATIVE(self) -> bool:
        """Property getter for N flag."""
        return self.FLAGS & Flag.NEGATIVE.value > 0

    @property
    def OVERFLOW(self) -> bool:
        """Property getter for O flag."""
        return self.FLAGS & Flag.OVERFLOW.value > 0

    @property
    def UNUSED(self) -> bool:
        """Property getter for U flag."""
        return self.FLAGS & Flag.UNUSED.value > 0

    @property
    def BREAK(self) -> bool:
        """Property getter for B flag."""
        return self.FLAGS & Flag.BREAK.value > 0

    @property
    def DECIMAL(self) -> bool:
        """Property getter for D flag."""
        return self.FLAGS & Flag.DECIMAL.value > 0

    @property
    def INTERRUPT(self) -> bool:
        """Property getter for I flag."""
        return self.FLAGS & Flag.INTERRUPT.value > 0

    @property
    def CARRY(self) -> bool:
        """Property getter for C flag."""
        return self.FLAGS & Flag.CARRY.value > 0

    @property
    def ZERO(self) -> bool:
        """Property getter for Z flag."""
        return self.FLAGS & Flag.ZERO.value > 0

    def flags2str(self) -> str:
        """Convert flags into nice looking string."""
        flag_str = "N" if self.NEGATIVE else "n"
        flag_str += "V" if self.OVERFLOW else "v"
        flag_str += "-"
        flag_str += "B" if self.BREAK else "b"
        flag_str += "D" if self.DECIMAL else "d"
        flag_str += "I" if self.INTERRUPT else "i"
        flag_str += "C" if self.CARRY else "c"
        flag_str += "Z" if self.ZERO else "z"
        return flag_str

    def __repr__(self) -> str:
        """Pretty print registers and flags."""
        flag_str = self.flags2str()
        return (
            f"Registers(A={self.A:02x}, X={self.X:02x}, Y={self.Y:02x}, PC={self.PC:04x},"
            f" SP={self.SP:04x}, FLAGS={flag_str})"
        )


def make_instruction_decorator(instructions: List[Instruction]):
    """Create the instruction decorator."""

    def InstructionDecorator(
        opcode=0, bytes=0, cycles=0, address_mode=AddressMode.NONE, mnemonic="???"
    ):
        def decorate(func):
            # opcode = int(func.__name__[5:9], base=16)
            instructions[opcode] = Instruction(
                opcode, cycles, bytes, mnemonic, address_mode, exec=func
            )
            return func

        return decorate

    return InstructionDecorator


def byte2bin(value: int) -> str:
    """Convert into to binary string."""
    return "{0:08b}".format(value & 0xFF)


def two_complement_to_dec(value: int) -> int:
    """Convert two-complement value into signed integer -128...127."""
    value &= 0xFF
    if value & 0x80 != 0:
        return (value & 0x7F) - 0x80
    return value


def dec_to_two_complement(value: int) -> int:
    """Convert signed decimal integer -128...127 into two-complement."""
    value &= 0xFF
    if value >= 0:
        return value
    return value - 0x80
