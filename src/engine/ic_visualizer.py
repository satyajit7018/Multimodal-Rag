"""Interactive Semiconductor IC Package SVG Visualizer.
Generates realistic vector SVG representations of electronics semiconductor packages
(DIP-8, DIP-16, DIP-28, QFN-32, TO-220) with color-coded pins and signal roles.
"""

from __future__ import annotations
from typing import Dict, Any, List

# Pin mappings for common ICs
IC_PINOUT_DATABASE: Dict[str, Dict[str, Any]] = {
    "ESP32": {
        "package": "QFN-48 / Module",
        "notch": "TOP",
        "left_pins": [
            ("3V3", "Power", "#EF4444"),
            ("EN", "Control", "#A855F7"),
            ("VP (IO36)", "Analog", "#FBBF24"),
            ("VN (IO39)", "Analog", "#FBBF24"),
            ("IO34", "Input", "#94A3B8"),
            ("IO35", "Input", "#94A3B8"),
            ("IO32", "GPIO", "#38BDF8"),
            ("IO33", "GPIO", "#38BDF8"),
            ("IO25", "DAC/GPIO", "#38BDF8"),
            ("IO26", "DAC/GPIO", "#38BDF8"),
            ("IO27", "GPIO", "#38BDF8"),
            ("IO14", "SPI/GPIO", "#38BDF8"),
            ("IO12", "SPI/GPIO", "#38BDF8"),
            ("GND", "Ground", "#475569"),
            ("IO13", "SPI/GPIO", "#38BDF8"),
        ],
        "right_pins": [
            ("GND", "Ground", "#475569"),
            ("IO23", "MOSI/SPI", "#34D399"),
            ("IO22", "SCL/I2C", "#38BDF8"),
            ("TX0", "UART_TX", "#F59E0B"),
            ("RX0", "UART_RX", "#F59E0B"),
            ("IO21", "SDA/I2C", "#34D399"),
            ("GND", "Ground", "#475569"),
            ("IO19", "MISO/SPI", "#34D399"),
            ("IO18", "SCK/SPI", "#38BDF8"),
            ("IO5", "CS/SPI", "#A855F7"),
            ("IO17", "UART2_TX", "#F59E0B"),
            ("IO16", "UART2_RX", "#F59E0B"),
            ("IO4", "1-Wire/GPIO", "#38BDF8"),
            ("IO2", "LED/GPIO", "#38BDF8"),
            ("IO15", "GPIO", "#38BDF8"),
        ],
    },
    "BME280": {
        "package": "DIP-6 Breakout",
        "notch": "TOP",
        "left_pins": [
            ("VCC (3.3V)", "Power", "#EF4444"),
            ("GND", "Ground", "#475569"),
            ("SCL", "I2C Clock", "#38BDF8"),
        ],
        "right_pins": [
            ("SDA", "I2C Data", "#34D399"),
            ("CSB", "SPI CS", "#A855F7"),
            ("SDO", "I2C Addr / SDO", "#FBBF24"),
        ],
    },
    "LM7805": {
        "package": "TO-220 3-Pin",
        "notch": "TOP",
        "left_pins": [
            ("Pin 1: VIN (7-25V)", "Power Input", "#EF4444"),
            ("Pin 2: GND (Common)", "Ground", "#475569"),
        ],
        "right_pins": [
            ("Pin 3: VOUT (5.0V Reg)", "Regulated Output", "#10B981"),
            ("Tab: GND (Heatsink)", "Ground / Thermal", "#475569"),
        ],
    },
    "PCA9685": {
        "package": "TSSOP-28",
        "notch": "TOP",
        "left_pins": [
            ("A0 (Addr)", "I2C Strapping", "#FBBF24"),
            ("A1 (Addr)", "I2C Strapping", "#FBBF24"),
            ("A2 (Addr)", "I2C Strapping", "#FBBF24"),
            ("A3 (Addr)", "I2C Strapping", "#FBBF24"),
            ("A4 (Addr)", "I2C Strapping", "#FBBF24"),
            ("LED0", "PWM Out", "#38BDF8"),
            ("LED1", "PWM Out", "#38BDF8"),
            ("GND", "Ground", "#475569"),
        ],
        "right_pins": [
            ("VCC (3.3-5V)", "Power", "#EF4444"),
            ("SDA", "I2C Data", "#34D399"),
            ("SCL", "I2C Clock", "#38BDF8"),
            ("/OE", "Output Enable", "#A855F7"),
            ("A5 (Addr)", "I2C Strapping", "#FBBF24"),
            ("LED15", "PWM Out", "#38BDF8"),
            ("LED14", "PWM Out", "#38BDF8"),
            ("V+ (Servo)", "Power Servo Rail", "#EF4444"),
        ],
    },
    "INA219": {
        "package": "SOT-23-8",
        "notch": "TOP",
        "left_pins": [
            ("A1 (Addr)", "I2C Strapping", "#FBBF24"),
            ("A0 (Addr)", "I2C Strapping", "#FBBF24"),
            ("SDA", "I2C Data", "#34D399"),
            ("SCL", "I2C Clock", "#38BDF8"),
        ],
        "right_pins": [
            ("VS (3.3-5V)", "Power", "#EF4444"),
            ("GND", "Ground", "#475569"),
            ("VIN+", "High-Side Bus+", "#EF4444"),
            ("VIN-", "Load Shunt-", "#F59E0B"),
        ],
    },
}


def generate_chip_svg(chip_name: str) -> str:
    """Renders a semiconductor IC package SVG vector graphic with color-coded pins."""
    data = IC_PINOUT_DATABASE.get(chip_name)
    if not data:
        # Generic IC fallback
        data = {
            "package": f"{chip_name} Standard Package",
            "notch": "TOP",
            "left_pins": [("Pin 1 (VCC)", "Power", "#EF4444"), ("Pin 2 (GND)", "Ground", "#475569"), ("Pin 3 (SIG)", "Signal", "#38BDF8")],
            "right_pins": [("Pin 4 (OUT)", "Output", "#34D399"), ("Pin 5 (CTRL)", "Control", "#A855F7"), ("Pin 6 (NC)", "No Connect", "#94A3B8")],
        }

    left_pins = data["left_pins"]
    right_pins = data["right_pins"]
    max_pins_side = max(len(left_pins), len(right_pins))

    # SVG layout geometry
    pin_height = 24
    pin_spacing = 10
    body_width = 180
    body_height = max(160, max_pins_side * (pin_height + pin_spacing) + 40)
    svg_width = 460
    svg_height = body_height + 40
    chip_x = (svg_width - body_width) // 2
    chip_y = 20

    svg = [
        f'<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" xmlns="http://www.w3.org/2000/svg" style="background:#0F172A; border-radius:14px; border:1px solid rgba(255,255,255,0.1); font-family:Inter,sans-serif;">',
        '  <defs>',
        '    <linearGradient id="icBodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1E293B" />',
        '      <stop offset="100%" stop-color="#0F172A" />',
        '    </linearGradient>',
        '  </defs>',
        '',
        f'  <!-- IC Chip Body -->',
        f'  <rect x="{chip_x}" y="{chip_y}" width="{body_width}" height="{body_height}" rx="12" fill="url(#icBodyGrad)" stroke="#475569" stroke-width="2" />',
        '',
        f'  <!-- Orientation Notch -->',
        f'  <path d="M {chip_x + body_width//2 - 14} {chip_y} A 14 14 0 0 0 {chip_x + body_width//2 + 14} {chip_y}" fill="#0F172A" stroke="#475569" stroke-width="1.5" />',
        '',
        f'  <!-- Chip Label -->',
        f'  <text x="{svg_width//2}" y="{chip_y + body_height//2 - 8}" fill="#F8FAFC" font-size="15" font-weight="700" text-anchor="middle" font-family="Outfit, sans-serif">{chip_name}</text>',
        f'  <text x="{svg_width//2}" y="{chip_y + body_height//2 + 12}" fill="#94A3B8" font-size="10" font-weight="500" text-anchor="middle">{data["package"]}</text>',
    ]

    # Render Left Pins
    for idx, (p_name, p_role, p_color) in enumerate(left_pins):
        py = chip_y + 30 + idx * (pin_height + pin_spacing)
        # Lead wire
        svg.append(f'  <line x1="{chip_x - 30}" y1="{py + pin_height//2}" x2="{chip_x}" y2="{py + pin_height//2}" stroke="{p_color}" stroke-width="3" />')
        # Pin terminal box
        svg.append(f'  <rect x="{chip_x - 35}" y="{py}" width="35" height="{pin_height}" rx="3" fill="{p_color}" opacity="0.9" />')
        # Pin number text
        svg.append(f'  <text x="{chip_x - 18}" y="{py + 16}" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle">{idx + 1}</text>')
        # Pin label text outside
        svg.append(f'  <text x="{chip_x - 42}" y="{py + 16}" fill="{p_color}" font-size="10.5" font-weight="600" text-anchor="end">{p_name}</text>')

    # Render Right Pins
    for idx, (p_name, p_role, p_color) in enumerate(right_pins):
        py = chip_y + 30 + idx * (pin_height + pin_spacing)
        # Lead wire
        svg.append(f'  <line x1="{chip_x + body_width}" y1="{py + pin_height//2}" x2="{chip_x + body_width + 30}" y2="{py + pin_height//2}" stroke="{p_color}" stroke-width="3" />')
        # Pin terminal box
        svg.append(f'  <rect x="{chip_x + body_width}" y="{py}" width="35" height="{pin_height}" rx="3" fill="{p_color}" opacity="0.9" />')
        # Pin number text
        pin_num = len(left_pins) + idx + 1
        svg.append(f'  <text x="{chip_x + body_width + 18}" y="{py + 16}" fill="#FFFFFF" font-size="10" font-weight="700" text-anchor="middle">{pin_num}</text>')
        # Pin label text outside
        svg.append(f'  <text x="{chip_x + body_width + 42}" y="{py + 16}" fill="{p_color}" font-size="10.5" font-weight="600" text-anchor="start">{p_name}</text>')

    svg.append('</svg>')
    return "\n".join(svg)
