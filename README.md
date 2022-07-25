# Testing

## Opcode test organization

For each opcode test up to two sets of tests are implemented:

- Test command specific behaviour (eg. decimal mode for ADC/SBC)
- Test all available adressing modes

Adressing modes to test:

- Immediate
- Zero Page
- Zero Page, X
  -- With page overflow (address $00FF with X=$01 => $0000)
- Absolute
- Absolute, X
  -- With memory wrapping (address $FFFF with X=$01 => $0000)
- Absolute, Y
  -- With memory wrapping
- Indirect, X
  -- With memory wrapping
- Indirect, Y
  -- With memory wrapping
