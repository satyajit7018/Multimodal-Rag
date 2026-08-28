"""Multi-Component Circuit Compatibility Engine.
Performs automated multi-part engineering validations:
1. I2C Address Collision Detection & Address Strapping Recommendations
2. Logic-Level Voltage Compatibility (3.3V vs 5.0V Level Shifting Requirements)
3. Power Budgeting & Regulator Load Checking
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

# Known component electrical metadata library (derived from datasheets)
COMPONENT_REGISTRY = {
    "ESP32": {
        "type": "MCU",
        "family": "Microcontroller",
        "voltage": 3.3,
        "5v_tolerant": False,
        "i2c_addresses": [],
        "max_gpio_current_ma": 40,
        "default_i2c_pins": {"SDA": "GPIO21", "SCL": "GPIO22"},
        "default_spi_pins": {"MOSI": "GPIO23", "MISO": "GPIO19", "SCK": "GPIO18", "CS": "GPIO5"},
        "default_uart_pins": {"TX": "GPIO1", "RX": "GPIO3"},
    },
    "RP2040": {
        "type": "MCU",
        "family": "Microcontroller",
        "voltage": 3.3,
        "5v_tolerant": False,
        "i2c_addresses": [],
        "max_gpio_current_ma": 16,
        "default_i2c_pins": {"SDA": "GPIO0", "SCL": "GPIO1"},
        "default_spi_pins": {"MOSI": "GPIO19", "MISO": "GPIO16", "SCK": "GPIO18", "CS": "GPIO17"},
        "default_uart_pins": {"TX": "GPIO0", "RX": "GPIO1"},
    },
    "STM32F103": {
        "type": "MCU",
        "family": "Microcontroller",
        "voltage": 3.3,
        "5v_tolerant": True,  # FT (5V tolerant) pins
        "i2c_addresses": [],
        "max_gpio_current_ma": 25,
        "default_i2c_pins": {"SDA": "PB7", "SCL": "PB6"},
        "default_spi_pins": {"MOSI": "PA7", "MISO": "PA6", "SCK": "PA5", "CS": "PA4"},
        "default_uart_pins": {"TX": "PA9", "RX": "PA10"},
    },
    "ATmega328P": {
        "type": "MCU",
        "family": "Microcontroller",
        "voltage": 5.0,
        "5v_tolerant": True,
        "i2c_addresses": [],
        "max_gpio_current_ma": 40,
        "default_i2c_pins": {"SDA": "PC4 / A4", "SCL": "PC5 / A5"},
        "default_spi_pins": {"MOSI": "PB3 / D11", "MISO": "PB4 / D12", "SCK": "PB5 / D13", "CS": "PB2 / D10"},
        "default_uart_pins": {"TX": "PD1 / D1", "RX": "PD0 / D0"},
    },
    "BME280": {
        "type": "Sensor",
        "family": "Environmental Sensor",
        "voltage": 3.3,
        "voltage_range": (1.71, 3.6),
        "i2c_addresses": ["0x76", "0x77"],
        "default_i2c": "0x76",
        "current_ma": 0.5,
        "interface": "I2C/SPI",
    },
    "MPU6050": {
        "type": "Sensor",
        "family": "Motion Sensor",
        "voltage": 3.3,
        "voltage_range": (2.375, 3.46),
        "i2c_addresses": ["0x68", "0x69"],
        "default_i2c": "0x68",
        "current_ma": 3.9,
        "interface": "I2C",
    },
    "PCA9685": {
        "type": "Actuator Controller",
        "family": "PWM Controller",
        "voltage": 3.3,
        "voltage_range": (2.3, 5.5),
        "i2c_addresses": ["0x40", "0x41", "0x42", "0x43", "0x44", "0x45", "0x46", "0x47"],
        "default_i2c": "0x40",
        "current_ma": 15.0,
        "interface": "I2C",
    },
    "ADS1115": {
        "type": "ADC",
        "family": "Converter",
        "voltage": 3.3,
        "voltage_range": (2.0, 5.5),
        "i2c_addresses": ["0x48", "0x49", "0x4A", "0x4B"],
        "default_i2c": "0x48",
        "current_ma": 0.2,
        "interface": "I2C",
    },
    "INA219": {
        "type": "Sensor",
        "family": "Power Monitor",
        "voltage": 3.3,
        "voltage_range": (3.0, 5.5),
        "i2c_addresses": ["0x40", "0x41", "0x44", "0x45"],
        "default_i2c": "0x40",
        "current_ma": 1.0,
        "interface": "I2C",
    },
    "VL53L0X": {
        "type": "Sensor",
        "family": "Distance Sensor",
        "voltage": 2.8,
        "voltage_range": (2.6, 3.5),
        "i2c_addresses": ["0x29"],
        "default_i2c": "0x29",
        "current_ma": 20.0,
        "interface": "I2C",
    },
    "DHT22": {
        "type": "Sensor",
        "family": "Temperature/Humidity Sensor",
        "voltage": 5.0,
        "voltage_range": (3.3, 6.0),
        "i2c_addresses": [],
        "current_ma": 1.5,
        "interface": "1-Wire GPIO",
    },
    "DS18B20": {
        "type": "Sensor",
        "family": "Temperature Sensor",
        "voltage": 3.3,
        "voltage_range": (3.0, 5.5),
        "i2c_addresses": [],
        "current_ma": 1.0,
        "interface": "1-Wire",
    },
    "MAX485": {
        "type": "Transceiver",
        "family": "RS-485 Interface",
        "voltage": 5.0,
        "voltage_range": (4.75, 5.25),
        "i2c_addresses": [],
        "current_ma": 30.0,
        "interface": "UART Half-Duplex",
    },
    "MCP2515": {
        "type": "Controller",
        "family": "CAN Bus Interface",
        "voltage": 5.0,
        "voltage_range": (2.7, 5.5),
        "i2c_addresses": [],
        "current_ma": 10.0,
        "interface": "SPI",
    },
    "L298N": {
        "type": "Driver",
        "family": "Motor Driver",
        "voltage": 5.0,
        "motor_voltage_max": 46.0,
        "i2c_addresses": [],
        "current_ma": 2000.0,
        "interface": "GPIO PWM / Direction",
    },
    "TB6612FNG": {
        "type": "Driver",
        "family": "Motor Driver",
        "voltage": 3.3,
        "motor_voltage_max": 13.5,
        "i2c_addresses": [],
        "current_ma": 1200.0,
        "interface": "GPIO PWM / Direction",
    },
    "A4988": {
        "type": "Driver",
        "family": "Stepper Driver",
        "voltage": 3.3,
        "motor_voltage_max": 35.0,
        "i2c_addresses": [],
        "current_ma": 2000.0,
        "interface": "STEP / DIR GPIO",
    },
}


def validate_circuit_compatibility(components: List[str]) -> Dict[str, Any]:
    """Audits a multi-component selection for electrical, bus, and logic compatibility."""
    valid_components = [c for c in components if c in COMPONENT_REGISTRY]
    if not valid_components:
        return {"status": "error", "message": "No recognized components selected for audit."}

    warnings = []
    errors = []
    i2c_bus = {}
    total_current_ma = 0.0
    mcu = next((c for c in valid_components if COMPONENT_REGISTRY[c]["type"] == "MCU"), None)
    mcu_meta = COMPONENT_REGISTRY.get(mcu) if mcu else None

    for comp in valid_components:
        meta = COMPONENT_REGISTRY[comp]
        total_current_ma += meta.get("current_ma", 5.0)

        # 1. Check I2C Address Conflicts
        if meta.get("interface") == "I2C" or "I2C" in meta.get("interface", ""):
            default_addr = meta.get("default_i2c")
            if default_addr:
                if default_addr in i2c_bus:
                    conflicting_part = i2c_bus[default_addr]
                    alt_addresses = meta.get("i2c_addresses", [])
                    recommendation = f"Change address pin strapping for {comp} (options: {', '.join(alt_addresses)})"
                    errors.append({
                        "type": "I2C Address Collision",
                        "severity": "CRITICAL",
                        "details": f"{comp} and {conflicting_part} both default to I2C address {default_addr}.",
                        "recommendation": recommendation,
                    })
                else:
                    i2c_bus[default_addr] = comp

        # 2. Check Logic-Level Voltage Conflicts with Host MCU
        if mcu and mcu != comp:
            comp_volt = meta.get("voltage", 3.3)
            mcu_volt = mcu_meta.get("voltage", 3.3)
            is_ft = mcu_meta.get("5v_tolerant", False)

            if mcu_volt == 3.3 and comp_volt == 5.0 and not is_ft:
                warnings.append({
                    "type": "Logic Level Mismatch",
                    "severity": "WARNING",
                    "details": f"{mcu} is a 3.3V non-5V-tolerant MCU, but {comp} operates at 5.0V logic.",
                    "recommendation": "Use a bidirectional logic level shifter (e.g. BSS138 or TXS0108E) or 1k/2k resistor divider on digital inputs.",
                })
            elif mcu_volt == 5.0 and comp_volt < 3.6:
                warnings.append({
                    "type": "Overvoltage Risk",
                    "severity": "CRITICAL",
                    "details": f"{mcu} outputs 5.0V logic signals directly to {comp} which is rated for {comp_volt}V max.",
                    "recommendation": "Do not connect directly! Place a 5V to 3.3V level shifter to prevent permanent IC damage.",
                })

    # 3. Power Budget Warning
    if total_current_ma > 500.0:
        warnings.append({
            "type": "High Current Draw",
            "severity": "NOTICE",
            "details": f"Total estimated load is {total_current_ma:.1f} mA (exceeds typical USB 500mA limit).",
            "recommendation": "Provide an external dedicated power supply or buck converter (e.g. MP1584 / XL6009).",
        })

    is_valid = len(errors) == 0
    return {
        "status": "pass" if is_valid else "issues_detected",
        "selected_components": valid_components,
        "host_mcu": mcu,
        "total_estimated_current_ma": round(total_current_ma, 1),
        "i2c_bus_allocation": i2c_bus,
        "critical_errors": errors,
        "compatibility_warnings": warnings,
    }
