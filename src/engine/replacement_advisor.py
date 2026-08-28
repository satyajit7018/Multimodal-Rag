"""Component Replacement & Drop-in Upgrade Advisor.
Analyzes semiconductor components and recommends pin-compatible or superior
drop-in alternatives for energy efficiency, thermal performance, and modern features.
"""

from __future__ import annotations
from typing import List, Dict, Any

REPLACEMENT_DATABASE = {
    "LM7805": [
        {
            "replacement": "MP1584",
            "type": "Switching Buck Converter",
            "advantages": "92% efficiency (vs ~45% linear), 3A max output, wide 4.5V-28V input range, significantly lower heat dissipation.",
            "pin_compatibility": "Requires small 3-pin or module footprint; eliminates need for bulky heatsink.",
            "efficiency_gain": "+47%",
        },
        {
            "replacement": "AMS1117-5.0",
            "type": "Low Dropout (LDO) Linear Regulator",
            "advantages": "Lower dropout voltage (1.1V vs 2.0V), compact SOT-223 SMD footprint, 1A rating.",
            "pin_compatibility": "Surface-mount alternative with smaller board area.",
            "efficiency_gain": "+15%",
        }
    ],
    "L298N": [
        {
            "replacement": "TB6612FNG",
            "type": "Dual MOSFET H-Bridge Driver",
            "advantages": "MOSFET output stages with very low internal voltage drop (<0.2V vs ~2.0V in L298N bipolar transistors), 1.2A continuous / 3.2A peak, built-in thermal shutdown.",
            "pin_compatibility": "Logic-level compatible (3.3V / 5.0V), no bulky heatsink required.",
            "efficiency_gain": "+40%",
        },
        {
            "replacement": "DRV8833",
            "type": "Low-Voltage Dual H-Bridge Driver",
            "advantages": "Operates down to 2.7V for battery-powered projects, low RDS(on) (360 mΩ), integrated current regulation.",
            "pin_compatibility": "Compact module layout with dedicated sleep mode.",
            "efficiency_gain": "+38%",
        }
    ],
    "ATmega328P": [
        {
            "replacement": "RP2040",
            "type": "Dual-Core ARM Cortex-M0+ SoC",
            "advantages": "Dual cores at 133 MHz (vs 16 MHz 8-bit), 264 KB SRAM (vs 2 KB), programmable I/O (PIO), USB bootloader.",
            "pin_compatibility": "Requires 3.3V logic (non-5V tolerant).",
            "efficiency_gain": "+800% compute",
        },
        {
            "replacement": "STM32F103",
            "type": "32-bit ARM Cortex-M3 MCU",
            "advantages": "72 MHz clock, 64 KB Flash, 20 KB SRAM, 5V-tolerant GPIO pins on primary ports.",
            "pin_compatibility": "5V tolerant inputs simplify drop-in upgrade.",
            "efficiency_gain": "+450% compute",
        }
    ],
    "LM358": [
        {
            "replacement": "AD620",
            "type": "Low Cost Instrumentation Amplifier",
            "advantages": "High CMRR (100 dB minimum), low input offset voltage (50 uV), gain set with a single external resistor.",
            "pin_compatibility": "Standard 8-pin DIP / SOIC footprint.",
            "efficiency_gain": "High Precision",
        }
    ]
}


def get_replacement_recommendations(component_name: str) -> List[Dict[str, Any]]:
    """Returns list of modern alternatives and upgrade advice for a component."""
    return REPLACEMENT_DATABASE.get(component_name, [])
