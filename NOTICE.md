# NOTICE

This software is the original work of Christophe Knap (KnapTheBuilder)
and community contributors.

Original repository: https://github.com/KnapTheBuilder/ha-joyonway-p23b32
Original frame analyzer: https://knapthebuilder.github.io/joyonway-frame-analyzer/

## Attribution requirements (MIT-compatible)

Any redistribution, modification, fork, or derivative work of this
software, in source or binary form, MUST:

1. Retain this NOTICE file in its entirety
2. Retain the copyright headers in all source files
3. Display a visible attribution to the original author in the README
   of the derivative work, with a clickable link to the original
   repository above
4. Comply with the terms of the MIT License (see LICENSE file)

## Original protocol research and reverse engineering

The Joyonway P23B32 RS485 protocol decoding in this integration is the
result of collaborative reverse engineering by:

- Christophe Knap (KnapTheBuilder): integration architecture, frame
  captures on P23B32 V2 with PB554 panel, command frame validation,
  Frame Analyzer browser tool
- KDy: oscilloscope baud rate analysis, byte-level frame decoding,
  pseudo-escape mechanism documentation
- Gaet78: P69B133 reference integration, CRC-8 parameters
  (poly=0x07, init=0x71)
- Yannickt26: P20B29 protocol compatibility validation
- Neuro: P23B32 V2 ESP32 reverse engineering

Any derivative work building upon this protocol research must credit
these contributors in its own NOTICE or CREDITS file.

## License

This software is distributed under the MIT License. See the LICENSE
file at the root of the repository for the full text.

The MIT License grants broad reuse rights but REQUIRES preservation
of the copyright notice and license text in all copies or substantial
portions of the software.

Failure to comply with these attribution requirements constitutes a
violation of the MIT License terms and may be addressed via GitHub
DMCA takedown procedures.

---

Copyright (c) 2026 Christophe Knap (KnapTheBuilder)
All rights reserved under the MIT License.
