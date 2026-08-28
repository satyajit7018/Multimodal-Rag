"""Live Pin-to-Pin Wiring Assistant.
Generates exact wiring schematics, pull-up resistor recommendations,
Mermaid.js circuit diagrams, and pin connection tables between any host microcontroller and peripheral modules.
"""

from __future__ import annotations
from typing import List, Dict, Any
from src.engine.circuit_validator import COMPONENT_REGISTRY


def generate_wiring_plan(host_mcu: str, peripherals: List[str]) -> Dict[str, Any]:
    """Produces pin-to-pin connections, signal roles, and passive component requirements."""
    if host_mcu not in COMPONENT_REGISTRY:
        return {"status": "error", "message": f"Host MCU '{host_mcu}' not found in registry."}

    mcu_meta = COMPONENT_REGISTRY[host_mcu]
    wiring_table = []
    notes = []

    for periph in peripherals:
        if periph not in COMPONENT_REGISTRY or periph == host_mcu:
            continue

        p_meta = COMPONENT_REGISTRY[periph]
        interface = p_meta.get("interface", "")

        # 1. Power connections
        vcc_rail = "3.3V" if p_meta.get("voltage", 3.3) <= 3.6 else "5.0V"
        wiring_table.append({
            "Source Component": host_mcu,
            "Source Pin": f"{vcc_rail} Power Rail",
            "Target Component": periph,
            "Target Pin": "VCC / VDD / Pin 1",
            "Signal Type": "Power Supply",
            "Notes": f"Supply rail: {vcc_rail}",
        })
        wiring_table.append({
            "Source Component": host_mcu,
            "Source Pin": "GND",
            "Target Component": periph,
            "Target Pin": "GND / Ground",
            "Signal Type": "Ground",
            "Notes": "Common ground reference",
        })

        # 2. I2C Interface Wiring
        if "I2C" in interface:
            i2c_pins = mcu_meta.get("default_i2c_pins", {"SDA": "SDA", "SCL": "SCL"})
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": i2c_pins["SDA"],
                "Target Component": periph,
                "Target Pin": "SDA (Serial Data)",
                "Signal Type": "I2C Bus",
                "Notes": "Add 4.7kΩ pull-up to 3.3V if not on breakout",
            })
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": i2c_pins["SCL"],
                "Target Component": periph,
                "Target Pin": "SCL (Serial Clock)",
                "Signal Type": "I2C Bus",
                "Notes": "Add 4.7kΩ pull-up to 3.3V if not on breakout",
            })
            notes.append(f"I2C Default Address for {periph}: {p_meta.get('default_i2c', 'N/A')}")

        # 3. SPI Interface Wiring
        elif "SPI" in interface:
            spi_pins = mcu_meta.get("default_spi_pins", {"MOSI": "MOSI", "MISO": "MISO", "SCK": "SCK", "CS": "CS"})
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": spi_pins["MOSI"],
                "Target Component": periph,
                "Target Pin": "SI / MOSI / SDI",
                "Signal Type": "SPI Master Out",
                "Notes": "Data from MCU to peripheral",
            })
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": spi_pins["MISO"],
                "Target Component": periph,
                "Target Pin": "SO / MISO / SDO",
                "Signal Type": "SPI Master In",
                "Notes": "Data from peripheral to MCU",
            })
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": spi_pins["SCK"],
                "Target Component": periph,
                "Target Pin": "SCK / SCLK",
                "Signal Type": "SPI Clock",
                "Notes": "Clock synchronous line",
            })
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": spi_pins["CS"],
                "Target Component": periph,
                "Target Pin": "CS / /SS / Chip Select",
                "Signal Type": "SPI Chip Select",
                "Notes": "Active LOW chip select",
            })

        # 4. UART Interface Wiring
        elif "UART" in interface:
            uart_pins = mcu_meta.get("default_uart_pins", {"TX": "TX", "RX": "RX"})
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": uart_pins["TX"],
                "Target Component": periph,
                "Target Pin": "RX / DI / Data In",
                "Signal Type": "UART Transmit",
                "Notes": "Cross TX to RX",
            })
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": uart_pins["RX"],
                "Target Component": periph,
                "Target Pin": "TX / RO / Receiver Out",
                "Signal Type": "UART Receive",
                "Notes": "Cross RX to TX",
            })

        # 5. 1-Wire Interface
        elif "1-Wire" in interface:
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": "GPIO4 (or any Digital GPIO)",
                "Target Component": periph,
                "Target Pin": "DATA / DQ / Pin 2",
                "Signal Type": "1-Wire Bidirectional",
                "Notes": "Mandatory 4.7kΩ pull-up resistor to VCC required",
            })

        # 6. Motor / PWM Direction Lines
        elif "Motor" in interface or "STEP" in interface:
            wiring_table.append({
                "Source Component": host_mcu,
                "Source Pin": "PWM Pin (e.g. GPIO18 / GPIO19)",
                "Target Component": periph,
                "Target Pin": "PWM / STEP / IN1",
                "Signal Type": "PWM Control",
                "Notes": "Requires dedicated motor battery/power supply",
            })

    return {
        "status": "success",
        "host_mcu": host_mcu,
        "peripherals": peripherals,
        "wiring_table": wiring_table,
        "engineering_notes": notes,
    }


def generate_mermaid_circuit_diagram(host_mcu: str, peripherals: List[str]) -> str:
    """Generates Mermaid.js flow diagram string with color-coded signal buses."""
    lines = ["graph LR"]
    lines.append(f'    MCU["🧠 {host_mcu}"]:::mcuStyle')

    for idx, periph in enumerate(peripherals):
        if periph == host_mcu:
            continue
        p_id = f"P_{idx}"
        lines.append(f'    {p_id}["📦 {periph}"]:::periphStyle')

        w_plan = generate_wiring_plan(host_mcu, [periph])
        for w in w_plan.get("wiring_table", []):
            sig = w["Signal Type"]
            s_pin = w["Source Pin"].split()[0]
            t_pin = w["Target Pin"].split()[0]
            if "I2C" in sig:
                lines.append(f'    MCU -- "{s_pin}➔{t_pin} (I2C)" --> {p_id}')
            elif "SPI" in sig:
                lines.append(f'    MCU -- "{s_pin}➔{t_pin} (SPI)" --> {p_id}')
            elif "UART" in sig:
                lines.append(f'    MCU -- "{s_pin}➔{t_pin} (UART)" --> {p_id}')
            elif "Power" in sig:
                lines.append(f'    MCU -- "{s_pin}➔VCC" --> {p_id}')
            elif "Ground" in sig:
                lines.append(f'    MCU -- "GND➔GND" --> {p_id}')

    lines.append("    classDef mcuStyle fill:#2563EB,stroke:#1D4ED8,stroke-width:2px,color:#FFFFFF;")
    lines.append("    classDef periphStyle fill:#1E293B,stroke:#475569,stroke-width:2px,color:#FFFFFF;")
    return "\n".join(lines)
