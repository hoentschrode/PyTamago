"""6502 MPU."""
from typing import List, Optional
from .utils import (
    Instruction,
    DecodedInstruction,
    Opcode,
    make_instruction_decorator,
    Registers,
    Flag,
    AddressMode,
    two_complement_to_dec,
)


class MPU:
    """MPU definition."""

    # Memory locations
    MEM_STACK = 0x0100
    MEM_VECTOR_NMI = 0xFFFA
    MEM_VECTOR_RESET = 0xFFFC
    MEM_VECTOR_IRQ_BRK = 0xFFFE

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
        self._registers.SP = 0xFF
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

    def _get_word_at(self, address: int, allow_page_overflow=True) -> int:
        """Read word from memory, wraps at 0xffff."""
        if not allow_page_overflow:
            # Special behaviour for indirect JMP: Wraps at page end!
            high = (address & 0xFF00) + (((address & 0x00FF) + 1) & 0x00FF)
            return self._memory[address] + (self._memory[high] << 8)
        return self._memory[address] + (self._memory[(address + 1) & 0xFFFF] << 8)

    def _get_word_at_zeropage(self, address: int) -> int:
        """Retrieve word in zeropage, wraps at 0x00ff."""
        zeropage_address = address & 0xFF
        return self._memory[zeropage_address] + ((self._memory[(zeropage_address + 1) & 0xFF]) << 8)

    def _push(self, value):
        self._set_byte_at(self.MEM_STACK + self.registers.SP, value)
        self.registers.SP -= 1
        self.registers.SP &= 0xFF

    def _push_word(self, value: int):
        value &= 0xFFFF
        self._push((value >> 8) & 0xFF)
        self._push(value & 0xFF)

    def _pop(self) -> int:
        self.registers.SP += 1
        self.registers.SP &= 0xFF
        return self._get_byte_at(self.MEM_STACK + self.registers.SP)

    def _pop_word(self) -> int:
        low_byte = self._pop()
        high_byte = self._pop()
        return ((high_byte << 8) + low_byte) & 0xFFFF

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
        raise NotImplementedError("Opcode not implementen!")

    def _get_effective_address(self, instruction: DecodedInstruction) -> Optional[int]:
        """
        Decode address mode and return effective address. None if no address is involved.

        Checks for page boundary crossing too and adds additional cycle
        """
        if instruction.address_mode in [
            AddressMode.NONE,
            AddressMode.ACCUMULATOR,
            AddressMode.IMMEDIATE,
            AddressMode.IMPLIED,
        ]:
            return None
        elif instruction.address_mode in [AddressMode.ZEROPAGE, AddressMode.ABSOLUTE]:
            return instruction.operand
        elif instruction.address_mode == AddressMode.ZEROPAGE_X:
            return (instruction.operand + self._registers.X) & 0xFF
        elif instruction.address_mode == AddressMode.ZEROPAGE_Y:
            return (instruction.operand + self._registers.Y) & 0xFF
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
        elif instruction.address_mode == AddressMode.INDIRECT:
            return self._get_word_at(instruction.operand, False) & 0xFFFF
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
        elif instruction.address_mode in [
            AddressMode.IMMEDIATE,
            AddressMode.BRANCH,
        ]:
            return instruction.operand

        address = self._get_effective_address(instruction)
        if address is None:
            return None
        elif instruction.address_mode == AddressMode.INDIRECT:
            return address

        return self._get_byte_at(address)

    def _modify_pc_for_conditional_branch(
        self, condition: bool, instruction: DecodedInstruction
    ) -> None:
        """
        Modify PC according to condition.

        Calculates additional cycles on page boundary crossings too.
        """
        if condition:
            instruction.extra_cycles += 1
            displacement = two_complement_to_dec(self._get_decoded_value(instruction))
            address = self.registers.PC + displacement
            # PC already moved !
            if (self.registers.PC - 2) & 0xFF00 != address & 0xFF00:
                instruction.extra_cycles += 1
            self.registers.PC = address & 0xFFFF

    def _cmp_x(self, register_value: int, value_to_compare: int):
        """Compare a value to a register value and set CZN-flags accordingly."""
        self.registers.modify_flag(Flag.CARRY, register_value >= value_to_compare)
        self.registers.modify_nz_flags((register_value - value_to_compare))

    @InstructionDecorator(
        "ADC",
        [
            Opcode(0x69, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0x65, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0x75, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0x6D, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0x7D, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0x79, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0x61, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0x71, 2, 5, AddressMode.INDIRECT_Y),
        ],
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
        "AND",
        [
            Opcode(0x29, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0x25, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0x35, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0x2D, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0x3D, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0x39, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0x21, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0x31, 2, 5, AddressMode.INDIRECT_Y),
        ],
    )
    def inst_AND(self, instruction: DecodedInstruction):
        """AND (bitwise AND with accumulator)."""
        self._registers.A &= self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        "ASL",
        [
            Opcode(0x0A, 1, 2, AddressMode.ACCUMULATOR),
            Opcode(0x06, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0x16, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0x0E, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0x1E, 3, 7, AddressMode.ABSOLUTE_X),
        ],
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
        self.registers.modify_flag(Flag.CARRY, (value & 0b1000_0000) != 0)
        value = (value << 1) & 0xFF
        self._registers.modify_nz_flags(value)

        # Write
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            self.registers.A = value
        else:
            self._set_byte_at(address, value)

    @InstructionDecorator(
        "BIT",
        [
            Opcode(0x24, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0x2C, 3, 4, AddressMode.ABSOLUTE),
        ],
    )
    def inst_BIT(self, instruction: DecodedInstruction):
        """BIT (test BITs)."""
        value = self._get_decoded_value(instruction)
        self.registers.modify_flag(Flag.ZERO, (self.registers.A & value) == 0)
        self.registers.modify_flag(Flag.NEGATIVE, (value & Flag.NEGATIVE.value) != 0)
        self.registers.modify_flag(Flag.OVERFLOW, (value & Flag.OVERFLOW.value) != 0)

    @InstructionDecorator("BPL", [Opcode(0x10, 2, 2, AddressMode.BRANCH)])
    def inst_BPL(self, instruction: DecodedInstruction):
        """BPL (Branch on PLus)."""
        self._modify_pc_for_conditional_branch(not self.registers.NEGATIVE, instruction)

    @InstructionDecorator("BMI", [Opcode(0x30, 2, 2, AddressMode.BRANCH)])
    def inst_BMI(self, instruction: DecodedInstruction):
        """BMI (Branch on MInus)."""
        self._modify_pc_for_conditional_branch(self.registers.NEGATIVE, instruction)

    @InstructionDecorator("BVC", [Opcode(0x50, 2, 2, AddressMode.BRANCH)])
    def inst_BVC(self, instruction: DecodedInstruction):
        """Branch on oVerflow Clear."""
        self._modify_pc_for_conditional_branch(not self.registers.OVERFLOW, instruction)

    @InstructionDecorator("BVS", [Opcode(0x70, 2, 2, AddressMode.BRANCH)])
    def inst_BVS(self, instruction: DecodedInstruction):
        """Branch on oVerflow Set."""
        self._modify_pc_for_conditional_branch(self.registers.OVERFLOW, instruction)

    @InstructionDecorator("BCC", [Opcode(0x90, 2, 2, AddressMode.BRANCH)])
    def inst_BCC(self, instruction: DecodedInstruction):
        """Branch on Carry Clear."""
        self._modify_pc_for_conditional_branch(not self.registers.CARRY, instruction)

    @InstructionDecorator("BCS", [Opcode(0xB0, 2, 2, AddressMode.BRANCH)])
    def inst_BCS(self, instruction: DecodedInstruction):
        """Branch on Carry Set."""
        self._modify_pc_for_conditional_branch(self.registers.CARRY, instruction)

    @InstructionDecorator("BNE", [Opcode(0xD0, 2, 2, AddressMode.BRANCH)])
    def inst_BNE(self, instruction: DecodedInstruction):
        """Branch on Not Equal."""
        self._modify_pc_for_conditional_branch(not self.registers.ZERO, instruction)

    @InstructionDecorator("BEQ", [Opcode(0xF0, 2, 2, AddressMode.BRANCH)])
    def inst_BEQ(self, instruction: DecodedInstruction):
        """Branch on EQual."""
        self._modify_pc_for_conditional_branch(self.registers.ZERO, instruction)

    @InstructionDecorator("BRK", [Opcode(0x00, 1, 2, AddressMode.IMPLIED)])
    def inst_BRK(self, instruction: DecodedInstruction):
        """BReaK."""
        self.registers.PC += 1
        self.registers.PC &= 0xFFFF
        self._push_word(self.registers.PC)

        self.registers.set_flag(Flag.BREAK)
        self._push(self.registers.FLAGS | Flag.UNUSED.value)
        self._registers.set_flag(Flag.INTERRUPT)
        self._registers.PC = self._get_word_at(self.MEM_VECTOR_IRQ_BRK)

    @InstructionDecorator("CLC", [Opcode(0x18, 1, 2, AddressMode.IMPLIED)])
    def inst_CLC(self, instruction: DecodedInstruction):
        """CLC (CLear Carry)."""
        self.registers.reset_flag(Flag.CARRY)

    @InstructionDecorator("CLD", [Opcode(0xD8, 1, 2, AddressMode.IMPLIED)])
    def inst_CLD(self, instruction: DecodedInstruction):
        """CLD (CLear Decimal)."""
        self.registers.reset_flag(Flag.DECIMAL)

    @InstructionDecorator("CLI", [Opcode(0x58, 1, 2, AddressMode.IMPLIED)])
    def inst_CLI(self, instruction: DecodedInstruction):
        """CLI (CLear Interrupt)."""
        self.registers.reset_flag(Flag.INTERRUPT)

    @InstructionDecorator("CLV", [Opcode(0xB8, 1, 2, AddressMode.IMPLIED)])
    def inst_CLV(self, instruction: DecodedInstruction):
        """CLV (CLear oVerflow)."""
        self.registers.reset_flag(Flag.OVERFLOW)

    @InstructionDecorator(
        "CMP",
        [
            Opcode(0xC9, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xC5, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xD5, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0xCD, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0xDD, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0xD9, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0xC1, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0xD1, 2, 5, AddressMode.INDIRECT_Y),
        ],
    )
    def inst_CMP(self, instruction: DecodedInstruction):
        """CMP (CoMPare accumulator)."""
        value = self._get_decoded_value(instruction)
        self._cmp_x(self.registers.A, value)

    @InstructionDecorator(
        "CPX",
        [
            Opcode(0xE0, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xE4, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xEC, 3, 4, AddressMode.ABSOLUTE),
        ],
    )
    def inst_CPX(self, instruction: DecodedInstruction):
        """CPX (ComPare X register)."""
        value = self._get_decoded_value(instruction)
        self._cmp_x(self.registers.X, value)

    @InstructionDecorator(
        "CPY",
        [
            Opcode(0xC0, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xC4, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xCC, 3, 4, AddressMode.ABSOLUTE),
        ],
    )
    def inst_CPY(self, instruction: DecodedInstruction):
        """CPY (ComPare Y register)."""
        value = self._get_decoded_value(instruction)
        self._cmp_x(self.registers.Y, value)

    @InstructionDecorator(
        "DEC",
        [
            Opcode(0xC6, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0xD6, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0xCE, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0xDE, 3, 7, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_DEC(self, instruction: DecodedInstruction):
        """DEC (DECrement memory)."""
        address = self._get_effective_address(instruction)
        value = (self._get_byte_at(address) - 1) & 0xFF
        self.registers.modify_nz_flags(value)
        self._set_byte_at(address, value)

    @InstructionDecorator("DEX", [Opcode(0xCA, 1, 2, AddressMode.IMPLIED)])
    def inst_DEX(self, instruction: DecodedInstruction):
        """DEX (DEcrement X)."""
        self.registers.X = (self.registers.X - 1) & 0xFF
        self.registers.modify_nz_flags(self._registers.X)

    @InstructionDecorator("DEY", [Opcode(0x88, 1, 2, AddressMode.IMPLIED)])
    def inst_DEY(self, instruction: DecodedInstruction):
        """DEY (DEcrement Y)."""
        self.registers.Y = (self.registers.Y - 1) & 0xFF
        self.registers.modify_nz_flags(self._registers.Y)

    @InstructionDecorator(
        "EOR",
        [
            Opcode(0x49, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0x45, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0x55, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0x4D, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0x5D, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0x59, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0x41, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0x51, 2, 5, AddressMode.INDIRECT_Y),
        ],
    )
    def inst_EOR(self, instruction: DecodedInstruction):
        """EOR (bitwise Exclusive OR)."""
        self._registers.A ^= self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        "INC",
        [
            Opcode(0xE6, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0xF6, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0xEE, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0xFE, 3, 7, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_INC(self, instruction: DecodedInstruction):
        """INC (INCrement memory)."""
        address = self._get_effective_address(instruction)
        value = (self._get_byte_at(address) + 1) & 0xFF
        self.registers.modify_nz_flags(value)
        self._set_byte_at(address, value)

    @InstructionDecorator("INX", [Opcode(0xE8, 1, 2, AddressMode.IMPLIED)])
    def inst_INX(self, instruction: DecodedInstruction):
        """INX (INcrement X)."""
        self.registers.X = (self.registers.X + 1) & 0xFF
        self.registers.modify_nz_flags(self._registers.X)

    @InstructionDecorator("INY", [Opcode(0xC8, 1, 2, AddressMode.IMPLIED)])
    def inst_INY(self, instruction: DecodedInstruction):
        """INY (INcrement Y)."""
        self.registers.Y = (self.registers.Y + 1) & 0xFF
        self.registers.modify_nz_flags(self._registers.Y)

    @InstructionDecorator(
        "JMP",
        [
            Opcode(0x4C, 3, 3, AddressMode.ABSOLUTE),
            Opcode(0x6C, 3, 4, AddressMode.INDIRECT),
        ],
    )
    def inst_JMP(self, instruction: DecodedInstruction):
        """JMP (JuMP)."""
        self.registers.PC = self._get_effective_address(instruction)

    @InstructionDecorator("JSR", [Opcode(0x20, 3, 6, AddressMode.ABSOLUTE)])
    def inst_JSR(self, instruction: DecodedInstruction):
        """JSR (Jump to SubRoutine)."""
        self._push_word(self.registers.PC - 1)
        self.registers.PC = self._get_effective_address(instruction)

    @InstructionDecorator(
        "LDA",
        [
            Opcode(0xA9, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xA5, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xB5, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0xAD, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0xBD, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0xB9, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0xA1, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0xB1, 2, 5, AddressMode.INDIRECT_Y),
        ],
    )
    def inst_LDA(self, instruction: DecodedInstruction):
        """LDA (LoaD Accumulator)."""
        self._registers.A = self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        "LDX",
        [
            Opcode(0xA2, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xA6, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xB6, 2, 4, AddressMode.ZEROPAGE_Y),
            Opcode(0xAE, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0xBE, 3, 4, AddressMode.ABSOLUTE_Y),
        ],
    )
    def inst_LDX(self, instruction: DecodedInstruction):
        """LDX (LoaD X register)."""
        self._registers.X = self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.X)

    @InstructionDecorator(
        "LDY",
        [
            Opcode(0xA0, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0xA4, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0xB4, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0xAC, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0xBC, 3, 4, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_LDY(self, instruction: DecodedInstruction):
        """LDY (LoaD Y register)."""
        self._registers.Y = self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.Y)

    @InstructionDecorator(
        "LSR",
        [
            Opcode(0x4A, 1, 2, AddressMode.ACCUMULATOR),
            Opcode(0x46, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0x56, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0x4E, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0x5E, 3, 7, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_LSR(self, instruction: DecodedInstruction):
        """LSR (Logical Shift Right)."""
        # Fetch
        address = None
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            value = self.registers.A
        else:
            address = self._get_effective_address(instruction)
            value = self._get_byte_at(address)

        # Do
        self.registers.modify_flag(Flag.CARRY, (value & 0x01) != 0)
        value = (value & 0xFF) >> 1
        self.registers.modify_nz_flags(value)

        # Write
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            self._registers.A = value
        else:
            self._set_byte_at(address, value)

    @InstructionDecorator("NOP", [Opcode(0xEA, 1, 2, AddressMode.IMPLIED)])
    def inst_NOP(self, instruction: DecodedInstruction):
        """NOP (No OPeration)."""
        pass

    @InstructionDecorator(
        "ORA",
        [
            Opcode(0x09, 2, 2, AddressMode.IMMEDIATE),
            Opcode(0x05, 2, 3, AddressMode.ZEROPAGE),
            Opcode(0x15, 2, 4, AddressMode.ZEROPAGE_X),
            Opcode(0x0D, 3, 4, AddressMode.ABSOLUTE),
            Opcode(0x1D, 3, 4, AddressMode.ABSOLUTE_X),
            Opcode(0x19, 3, 4, AddressMode.ABSOLUTE_Y),
            Opcode(0x01, 2, 6, AddressMode.INDIRECT_X),
            Opcode(0x11, 2, 5, AddressMode.INDIRECT_Y),
        ],
    )
    def inst_ORA(self, instruction: DecodedInstruction):
        """ORA (bitwise OR with Accumulator)."""
        self._registers.A |= self._get_decoded_value(instruction)
        self._registers.modify_nz_flags(self._registers.A)

    @InstructionDecorator(
        "ROL",
        [
            Opcode(0x2A, 1, 2, AddressMode.ACCUMULATOR),
            Opcode(0x26, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0x36, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0x2E, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0x3E, 3, 7, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_ROL(self, instruction: DecodedInstruction):
        """ROL (ROtate Left)."""
        # Fetch
        address = None
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            value = self.registers.A
        else:
            address = self._get_effective_address(instruction)
            value = self._get_byte_at(address)

        # Do
        carry_in = 1 if self.registers.CARRY else 0
        self.registers.modify_flag(Flag.CARRY, (value & 0x80) != 0)
        value = ((value << 1) & 0xFF) | carry_in
        self.registers.modify_nz_flags(value)

        # Write
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            self._registers.A = value
        else:
            self._set_byte_at(address, value)

    @InstructionDecorator(
        "ROR",
        [
            Opcode(0x6A, 1, 2, AddressMode.ACCUMULATOR),
            Opcode(0x66, 2, 5, AddressMode.ZEROPAGE),
            Opcode(0x76, 2, 6, AddressMode.ZEROPAGE_X),
            Opcode(0x6E, 3, 6, AddressMode.ABSOLUTE),
            Opcode(0x7E, 3, 7, AddressMode.ABSOLUTE_X),
        ],
    )
    def inst_ROR(self, instruction: DecodedInstruction):
        """ROR (ROtate Right)."""
        # Fetch
        address = None
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            value = self.registers.A
        else:
            address = self._get_effective_address(instruction)
            value = self._get_byte_at(address)

        # Do
        carry_in = 0x80 if self.registers.CARRY else 0
        self.registers.modify_flag(Flag.CARRY, (value & 0x01) != 0)
        value = ((value >> 1) & 0xFF) | carry_in
        self.registers.modify_nz_flags(value)

        # Write
        if instruction.address_mode == AddressMode.ACCUMULATOR:
            self._registers.A = value
        else:
            self._set_byte_at(address, value)

    @InstructionDecorator("RTI", [Opcode(0x40, 1, 6, AddressMode.IMPLIED)])
    def inst_RTI(self, instruction: DecodedInstruction):
        """RTI (ReTurn from Interrupt)."""
        self._registers.FLAGS = self._pop()
        self._registers.PC = self._pop_word()

    @InstructionDecorator("RTS", [Opcode(0x60, 1, 6, AddressMode.IMPLIED)])
    def inst_RTS(self, instruction: DecodedInstruction):
        """RTS (ReTurn from Subroutine)."""
        self._registers.PC = self._pop_word() + 1

    @InstructionDecorator("SEC", [Opcode(0x38, 1, 2, AddressMode.IMPLIED)])
    def inst_SEC(self, instruction: DecodedInstruction):
        """SEC (SEt Carry)."""
        self.registers.set_flag(Flag.CARRY)

    @InstructionDecorator("SED", [Opcode(0xF8, 1, 2, AddressMode.IMPLIED)])
    def inst_SED(self, instruction: DecodedInstruction):
        """SED (SEt Decimal)."""
        self.registers.set_flag(Flag.DECIMAL)

    @InstructionDecorator("SEI", [Opcode(0x78, 1, 2, AddressMode.IMPLIED)])
    def inst_SEI(self, instruction: DecodedInstruction):
        """SEI (SEt Interrupt)."""
        self.registers.set_flag(Flag.INTERRUPT)

    @InstructionDecorator("TAX", [Opcode(0xAA, 1, 2, AddressMode.IMPLIED)])
    def inst_TAX(self, instruction: DecodedInstruction):
        """TAX (Transfer A to X)."""
        self.registers.X = self.registers.A
        self.registers.modify_nz_flags(self.registers.X)

    @InstructionDecorator("TXA", [Opcode(0x8A, 1, 2, AddressMode.IMPLIED)])
    def inst_TXA(self, instruction: DecodedInstruction):
        """TXA (Transfer X to A)."""
        self.registers.A = self.registers.X
        self.registers.modify_nz_flags(self.registers.A)

    @InstructionDecorator("TAY", [Opcode(0xA8, 1, 2, AddressMode.IMPLIED)])
    def inst_TAA(self, instruction: DecodedInstruction):
        """TAY (Transfer A to Y)."""
        self.registers.Y = self.registers.A
        self.registers.modify_nz_flags(self.registers.Y)

    @InstructionDecorator("TYA", [Opcode(0x98, 1, 2, AddressMode.IMPLIED)])
    def inst_TYA(self, instruction: DecodedInstruction):
        """TYA (Transfer Y to A)."""
        self.registers.A = self.registers.Y
        self.registers.modify_nz_flags(self.registers.A)
