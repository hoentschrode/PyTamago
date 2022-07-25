"""6502 MPU."""
from email.headerregistry import Address
from typing import List, Optional
from .utils import (
    Instruction,
    DecodedInstruction,
    make_instruction_decorator,
    Registers,
    Flag,
    AddressMode,
)


class MPU:
    """MPU definition."""

    _instructions: List[Instruction] = [None] * (0xFF + 1)
    InstructionDecorator = make_instruction_decorator(_instructions)

    def __init__(self, memory, pc: int = 0x0000) -> None:
        """Initialize MPU (performs a reset too!)."""
        self._enrich_instructions()
        self._registers = Registers(A=0, X=0, Y=0, FLAGS=0, PC=0, SP=0)
        self._start_pc = pc
        self._elapsed_cycles = 0

        self._memory = memory
        self.reset()

    def _enrich_instructions(self):
        """Map all unmapped opcodes to ??? function."""
        for opcode in range(0xFF + 1):
            if not isinstance(self._instructions[opcode], Instruction):
                self._instructions[opcode] = Instruction(
                    opcode, 0, 1, "???", AddressMode.NONE, self.inst_not_implemented
                )

    def reset(self):
        """Perform MPU reset."""
        self._registers.PC = self._start_pc
        self._registers.SP = 0xFFFF
        self._registers.A = 0
        self._registers.X = 0
        self._registers.Y = 0

    def decode(self, address: int) -> DecodedInstruction:
        """Decode instruction at particular address."""
        instruction_opcode = self._get_byte_at(address)
        instruction = DecodedInstruction(**self._instructions[instruction_opcode].__dict__)
        instruction.address = address
        instruction.operand = self._fetch_operands(instruction)
        return instruction

    def step(self):
        """Execute instruction at PC."""
        instruction = self.decode(self._registers.PC)
        self._registers.PC += instruction.bytes
        instruction.exec(self, instruction)
        self._elapsed_cycles += instruction.cycles + instruction.extra_cycles

    def _fetch_operands(self, instruction: DecodedInstruction) -> Optional[int]:
        """Fetch instructions operands."""
        if instruction.bytes == 1:
            return None
        elif instruction.bytes == 2:
            return self._get_byte_at(instruction.address + 1)
        elif instruction.bytes == 3:
            return self._get_word_at(instruction.address + 1)
        raise ValueError(f"Invalid instruction size {instruction.bytes}")

    def _get_byte_at(self, address: int) -> int:
        """Read byte from memory."""
        return self._memory[address] & 0xFF

    def _set_byte_at(self, address: int, value: int) -> None:
        """Write byte to memory."""
        self._memory[address] = value & 0xFF

    def _get_word_at(self, address: int) -> int:
        """Read word from memory, wraps at 0xffff."""
        return self._memory[address] + (self._memory[(address + 1) & 0xFFFF] << 8)

    def _get_word_at_zeropage(self, address: int) -> int:
        """Retrieve word in zeropage, wraps at 0x00ff."""
        zeropage_address = address & 0xFF
        return self._memory[zeropage_address] + ((self._memory[(zeropage_address + 1) & 0xFF]) << 8)

    @property
    def registers(self) -> Registers:
        """Property getter for registers."""
        return self._registers

    @property
    def elapsed_cycles(self) -> int:
        """Property getter for elapsed cycles since power on."""
        return self._elapsed_cycles

    def inst_not_implemented(*args, **kwargs):
        """Do nothing. Just a dummy for unmapped opcodes."""
        return

    def _get_effective_address(self, instruction: DecodedInstruction) -> Optional[int]:
        """
        Decode address mode and return effective address. None if no address is involved.

        Checks for page boundary crossing too and adds additional cycle
        """
        if instruction.address_mode in [
            AddressMode.NONE,
            AddressMode.ACCUMULATOR,
            AddressMode.IMMEDIATE,
        ]:
            return None
        elif instruction.address_mode in [AddressMode.ZEROPAGE, AddressMode.ABSOLUTE]:
            return instruction.operand
        elif instruction.address_mode == AddressMode.ZEROPAGE_X:
            return (instruction.operand + self._registers.X) & 0xFF
        elif instruction.address_mode == AddressMode.ABSOLUTE_X:
            # Check for extra cycle on page boundary crossing
            if (instruction.operand & 0x00FF) + self._registers.X > 0xFF:
                instruction.extra_cycles = 1
            return (instruction.operand + self._registers.X) & 0xFFFF
        elif instruction.address_mode == AddressMode.ABSOLUTE_Y:
            # Check for extra cycle on page boundary crossing
            if (instruction.operand & 0x00FF) + self._registers.Y > 0xFF:
                instruction.extra_cycles = 1
            return (instruction.operand + self._registers.Y) & 0xFFFF
        elif instruction.address_mode == AddressMode.INDIRECT_X:
            return self._get_word_at_zeropage((instruction.operand + self._registers.X) & 0xFF)
        elif instruction.address_mode == AddressMode.INDIRECT_Y:
            addr = self._get_word_at_zeropage(instruction.operand)
            # Check for extra cycle on page boundary crossing
            if (addr & 0x00FF) + self._registers.Y > 0xFF:
                instruction.extra_cycles = 1
            return (addr + self._registers.Y) & 0xFFFF
        raise ValueError(f"Unsupported address mode {instruction.address_mode}!")

    def _get_decoded_value(self, instruction: DecodedInstruction) -> Optional[int]:
        """Decode adress mode and return referenced value."""
        if instruction.address_mode == AddressMode.NONE:
            return None
        elif instruction.address_mode == AddressMode.ACCUMULATOR:
            return self.registers.A
        elif instruction.address_mode == AddressMode.IMMEDIATE:
            return instruction.operand

        address = self._get_effective_address(instruction)
        if address is None:
            return None
        return self._get_byte_at(address)

    @InstructionDecorator(
        opcode=0x69, bytes=2, cycles=2, address_mode=AddressMode.IMMEDIATE, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x65, bytes=2, cycles=3, address_mode=AddressMode.ZEROPAGE, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x75, bytes=2, cycles=4, address_mode=AddressMode.ZEROPAGE_X, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x6D, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x7D, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_X, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x79, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_Y, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x61, bytes=2, cycles=6, address_mode=AddressMode.INDIRECT_X, mnemonic="ADC"
    )
    @InstructionDecorator(
        opcode=0x71, bytes=2, cycles=5, address_mode=AddressMode.INDIRECT_Y, mnemonic="ADC"
    )
    def inst_ADC(self, instruction: DecodedInstruction):
        """ADC (ADd with Carry)."""
        value = self._get_decoded_value(instruction)
        if self._registers.DECIMAL:
            # Decimal mode
            half_carry = 0
            decimal_carry_flag = False
            low_nibble_adjustment = 0
            low_nibble = (
                (value & 0x0F) + (self._registers.A & 0x0F) + (1 if self._registers.CARRY else 0)
            )
            if low_nibble > 9:
                half_carry = 1
                low_nibble_adjustment = 6

            high_nibble_adjustment = 0
            high_nibble = ((value >> 4) & 0x0F) + ((self._registers.A >> 4) & 0x0F) + half_carry
            if high_nibble > 9:
                decimal_carry_flag = True
                high_nibble_adjustment = 6

            # Non-decimal-adjusted result to evaluate flags
            low_nibble &= 0x0F
            high_nibble &= 0x0F
            result = (high_nibble << 4) + low_nibble
            self._registers.reset_flags([Flag.CARRY, Flag.OVERFLOW, Flag.NEGATIVE, Flag.ZERO])
            self._registers.modify_flag(Flag.CARRY, decimal_carry_flag)
            self._registers.modify_nz_flags(result)
            self._registers.modify_flag(
                Flag.OVERFLOW,
                (~(self._registers.A ^ value) & (self._registers.A ^ result)) & 0b1000_0000 > 0,
            )

            # Decimal adjustment for A
            low_nibble = (low_nibble + low_nibble_adjustment) & 0x0F
            high_nibble = (high_nibble + high_nibble_adjustment) & 0x0F
            self._registers.A = (high_nibble << 4) + low_nibble

        else:
            # Binary mode

            result = self._registers.A + value + (1 if self._registers.CARRY else 0)
            # Reset all affected flags C, V, N and Z
            self._registers.reset_flags([Flag.CARRY, Flag.OVERFLOW, Flag.NEGATIVE, Flag.ZERO])

            # Refer to: https://www.righto.com/2012/12/the-6502-overflow-flag-explained.html
            n7 = (self._registers.A & 0b1000_0000) != 0
            m7 = (value & 0b1000_0000) != 0
            c6 = ((self._registers.A & 0b0100_0000) >> 6) and ((value & 0b0100_0000) >> 6)
            self._registers.modify_flag(
                Flag.OVERFLOW, (not m7 and not n7 and c6) or (m7 and n7 and not c6)
            )

            self._registers.modify_flag(Flag.CARRY, result > 0xFF)
            self._registers.A = result & 0xFF
            self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        opcode=0x29, bytes=2, cycles=2, address_mode=AddressMode.IMMEDIATE, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x25, bytes=2, cycles=3, address_mode=AddressMode.ZEROPAGE, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x35, bytes=2, cycles=4, address_mode=AddressMode.ZEROPAGE_X, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x2D, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x3D, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_X, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x39, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_Y, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x21, bytes=2, cycles=6, address_mode=AddressMode.INDIRECT_X, mnemonic="AND"
    )
    @InstructionDecorator(
        opcode=0x31, bytes=2, cycles=5, address_mode=AddressMode.INDIRECT_Y, mnemonic="AND"
    )
    def inst_AND(self, instruction: DecodedInstruction):
        """AND (bitwise AND with accumulator)."""
        self._registers.A &= self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        opcode=0x0A, bytes=1, cycles=2, address_mode=AddressMode.ACCUMULATOR, mnemonic="ASL"
    )
    @InstructionDecorator(
        opcode=0x06, bytes=2, cycles=5, address_mode=AddressMode.ZEROPAGE, mnemonic="ASL"
    )
    @InstructionDecorator(
        opcode=0x16, bytes=2, cycles=6, address_mode=AddressMode.ZEROPAGE_X, mnemonic="ASL"
    )
    @InstructionDecorator(
        opcode=0x0E, bytes=3, cycles=6, address_mode=AddressMode.ABSOLUTE, mnemonic="ASL"
    )
    @InstructionDecorator(
        opcode=0x1E, bytes=3, cycles=7, address_mode=AddressMode.ABSOLUTE_X, mnemonic="ASL"
    )
    def inst_ASL(self, instruction: DecodedInstruction):
        """ASL (Arithmetic Shift Left)."""
        # Fetch
        address = None
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            value = self.registers.A
        else:
            address = self._get_effective_address(instruction)
            value = self._get_byte_at(address)

        # Do
        carry_in = 1 if self.registers.CARRY else 0
        self.registers.modify_flag(Flag.CARRY, (value & 0b1000_0000) != 0)
        value = ((value << 1) & 0xFF) + carry_in
        self._registers.modify_nz_flags(value)

        # Write
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            self.registers.A = value
        else:
            self._set_byte_at(address, value)

    @InstructionDecorator(
        opcode=0xA9, bytes=2, cycles=2, address_mode=AddressMode.IMMEDIATE, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xA5, bytes=2, cycles=3, address_mode=AddressMode.ZEROPAGE, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xB5, bytes=2, cycles=4, address_mode=AddressMode.ZEROPAGE_X, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xAD, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xBD, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_X, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xB9, bytes=3, cycles=4, address_mode=AddressMode.ABSOLUTE_Y, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xA1, bytes=2, cycles=6, address_mode=AddressMode.INDIRECT_X, mnemonic="LDA"
    )
    @InstructionDecorator(
        opcode=0xB1, bytes=2, cycles=5, address_mode=AddressMode.INDIRECT_Y, mnemonic="LDA"
    )
    def inst_LDA(self, instruction: DecodedInstruction):
        """LDA (LoaD Accumulator)."""
        self._registers.A = self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)