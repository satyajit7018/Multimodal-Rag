"""Multi-Component Circuit Compatibility Engine.
Performs automated multi-part engineering validations:
1. I2C Address Collision Detection & Address Strapping Recommendations
2. Logic-Level Voltage Compatibility (3.3V vs 5.0V Level Shifting Requirements)
3. Power Budgeting & Regulator Load Checking
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

# Complete 32-Component Electrical Metadata Library
COMPONENT_REGISTRY = {
    # 1. Microcontrollers & Wireless
    "ESP32": {
        "type": "MCU",
        "family": "Microcontrollers & Wireless",
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
        "family": "Microcontrollers & Wireless",
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
        "family": "Microcontrollers & Wireless",
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
        "family": "Microcontrollers & Wireless",
        "voltage": 5.0,
        "5v_tolerant": True,
        "i2c_addresses": [],
        "max_gpio_current_ma": 40,
        "default_i2c_pins": {"SDA": "PC4 / A4", "SCL": "PC5 / A5"},
        "default_spi_pins": {"MOSI": "PB3 / D11", "MISO": "PB4 / D12", "SCK": "PB5 / D13", "CS": "PB2 / D10"},
        "default_uart_pins": {"TX": "PD1 / D1", "RX": "PD0 / D0"},
    },
    "nRF52840": {
        "type": "MCU",
        "family": "Microcontrollers & Wireless",
        "voltage": 3.3,
        "5v_tolerant": False,
        "i2c_addresses": [],
        "max_gpio_current_ma": 15,
        "default_i2c_pins": {"SDA": "P0.26", "SCL": "P0.27"},
        "default_spi_pins": {"MOSI": "P0.20", "MISO": "P0.21", "SCK": "P0.19", "CS": "P0.17"},
        "default_uart_pins": {"TX": "P0.06", "RX": "P0.08"},
    },
    "ESP8266": {
        "type": "MCU",
        "family": "Microcontrollers & Wireless",
        "voltage": 3.3,
        "5v_tolerant": False,
        "i2c_addresses": [],
        "max_gpio_current_ma": 12,
        "default_i2c_pins": {"SDA": "GPIO4", "SCL": "GPIO5"},
        "default_spi_pins": {"MOSI": "GPIO13", "MISO": "GPIO12", "SCK": "GPIO14", "CS": "GPIO15"},
        "default_uart_pins": {"TX": "GPIO1", "RX": "GPIO3"},
    },

    # 2. Sensors & Converters
    "BME280": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "I2C / SPI",
        "default_i2c": "0x76",
        "i2c_addresses": ["0x76", "0x77"],
        "current_ma": 3.6,
    },
    "DHT22": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "1-Wire",
        "current_ma": 2.5,
    },
    "MPU6050": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "I2C",
        "default_i2c": "0x68",
        "i2c_addresses": ["0x68", "0x69"],
        "current_ma": 3.9,
    },
    "VL53L0X": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 2.8,
        "5v_tolerant": True,
        "interface": "I2C",
        "default_i2c": "0x29",
        "i2c_addresses": ["0x29"],
        "current_ma": 19.0,
    },
    "DS18B20": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "1-Wire",
        "current_ma": 1.5,
    },
    "INA219": {
        "type": "Sensor",
        "family": "Sensors & Converters",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "I2C",
        "default_i2c": "0x40",
        "i2c_addresses": ["0x40", "0x41", "0x44", "0x45"],
        "current_ma": 1.0,
    },

    # 3. Power Management & Regulators
    "LM7805": {
        "type": "Regulator",
        "family": "Power Management & Regulators",
        "voltage": 5.0,
        "input_voltage_range": "7.0V - 25.0V",
        "current_ma": 1500,
        "interface": "Power Supply",
    },
    "LM317": {
        "type": "Regulator",
        "family": "Power Management & Regulators",
        "voltage": "1.25V - 37V",
        "current_ma": 1500,
        "interface": "Power Supply",
    },
    "AMS1117": {
        "type": "Regulator",
        "family": "Power Management & Regulators",
        "voltage": 3.3,
        "input_voltage_range": "4.5V - 12.0V",
        "current_ma": 800,
        "interface": "Power Supply",
    },
    "TP4056": {
        "type": "Charger",
        "family": "Power Management & Regulators",
        "voltage": 4.2,
        "current_ma": 1000,
        "interface": "Power Supply",
    },
    "MP1584": {
        "type": "Buck Converter",
        "family": "Power Management & Regulators",
        "voltage": "0.8V - 20V",
        "input_voltage_range": "4.5V - 28.0V",
        "current_ma": 3000,
        "interface": "Power Supply",
    },
    "XL6009": {
        "type": "Boost Converter",
        "family": "Power Management & Regulators",
        "voltage": "5V - 35V",
        "current_ma": 4000,
        "interface": "Power Supply",
    },

    # 4. Motor Drivers & Controllers
    "L298N": {
        "type": "Driver",
        "family": "Motor Drivers & Actuators",
        "voltage": 5.0,
        "5v_tolerant": True,
        "interface": "GPIO / PWM",
        "current_ma": 2000,
    },
    "TB6612FNG": {
        "type": "Driver",
        "family": "Motor Drivers & Actuators",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "GPIO / PWM",
        "current_ma": 1200,
    },
    "A4988": {
        "type": "Driver",
        "family": "Motor Drivers & Actuators",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "STEP / DIR",
        "current_ma": 2000,
    },
    "DRV8833": {
        "type": "Driver",
        "family": "Motor Drivers & Actuators",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "GPIO / PWM",
        "current_ma": 1500,
    },
    "ULN2003A": {
        "type": "Driver",
        "family": "Motor Drivers & Actuators",
        "voltage": 5.0,
        "5v_tolerant": True,
        "interface": "GPIO Darlington",
        "current_ma": 500,
    },

    # 5. Signal Conditioning & Op-Amps
    "LM358": {
        "type": "Op-Amp",
        "family": "Signal Conditioning & Op-Amps",
        "voltage": 5.0,
        "current_ma": 20,
        "interface": "Analog",
    },
    "NE555": {
        "type": "Timer",
        "family": "Signal Conditioning & Op-Amps",
        "voltage": 5.0,
        "current_ma": 15,
        "interface": "Pulse / Timer",
    },
    "LM393": {
        "type": "Comparator",
        "family": "Signal Conditioning & Op-Amps",
        "voltage": 5.0,
        "current_ma": 2.5,
        "interface": "Analog / Open-Collector",
    },
    "ADS1115": {
        "type": "Converter",
        "family": "Signal Conditioning & Op-Amps",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "I2C",
        "default_i2c": "0x48",
        "i2c_addresses": ["0x48", "0x49", "0x4A", "0x4B"],
        "current_ma": 0.3,
    },
    "AD620": {
        "type": "Amp",
        "family": "Signal Conditioning & Op-Amps",
        "voltage": 5.0,
        "current_ma": 1.3,
        "interface": "Analog Instrumentation",
    },

    # 6. Communication & Interfaces
    "MAX485": {
        "type": "Transceiver",
        "family": "Communication & Interfaces",
        "voltage": 5.0,
        "5v_tolerant": False,
        "interface": "UART",
        "current_ma": 30.0,
    },
    "MCP2515": {
        "type": "Transceiver",
        "family": "Communication & Interfaces",
        "voltage": 5.0,
        "5v_tolerant": True,
        "interface": "SPI",
        "current_ma": 10.0,
    },
    "PCA9685": {
        "type": "Controller",
        "family": "Communication & Interfaces",
        "voltage": 3.3,
        "5v_tolerant": True,
        "interface": "I2C",
        "default_i2c": "0x40",
        "i2c_addresses": ["0x40", "0x41", "0x42", "0x43"],
        "current_ma": 20.0,
    },
    "CH340G": {
        "type": "Transceiver",
        "family": "Communication & Interfaces",
        "voltage": 5.0,
        "5v_tolerant": True,
        "interface": "USB-to-UART",
        "current_ma": 12.0,
    },
}


def validate_circuit_compatibility(selected_components: List[str]) -> Dict[str, Any]:
    """Evaluates a multi-component selection for electrical conflicts and provides mitigation advice."""
    critical_errors = []
    compatibility_warnings = []
    i2c_bus_allocation: Dict[str, str] = {}
    total_current_ma = 0.0

    host_mcu = None
    for c in selected_components:
        if c in COMPONENT_REGISTRY and COMPONENT_REGISTRY[c]["type"] == "MCU":
            host_mcu = c
            break

    mcu_voltage = COMPONENT_REGISTRY[host_mcu]["voltage"] if host_mcu else 3.3
    mcu_5v_tolerant = COMPONENT_REGISTRY[host_mcu].get("5v_tolerant", False) if host_mcu else False

    for comp in selected_components:
        if comp not in COMPONENT_REGISTRY:
            continue

        meta = COMPONENT_REGISTRY[comp]
        c_voltage = meta.get("voltage", 3.3)
        c_current = meta.get("current_ma", 0.0)
        c_interface = meta.get("interface", "")
        c_i2c_default = meta.get("default_i2c")

        if isinstance(c_current, (int, float)):
            total_current_ma += c_current

        # 1. Check I2C Address Collisions
        if c_i2c_default:
            if c_i2c_default in i2c_bus_allocation:
                existing_comp = i2c_bus_allocation[c_i2c_default]
                critical_errors.append({
                    "type": "I2C Address Collision",
                    "severity": "CRITICAL",
                    "details": f"{comp} and {existing_comp} both default to I2C address {c_i2c_default}.",
                    "recommendation": f"Change address pin strapping for {comp} (options: {', '.join(meta.get('i2c_addresses', []))})",
                })
            else:
                i2c_bus_allocation[c_i2c_default] = comp

        # 2. Check Logic-Level Mismatches
        if host_mcu and comp != host_mcu and isinstance(c_voltage, (int, float)):
            if c_voltage > mcu_voltage and not mcu_5v_tolerant:
                compatibility_warnings.append({
                    "type": "Logic Level Mismatch",
                    "severity": "WARNING",
                    "details": f"{comp} logic operates at {c_voltage}V while host {host_mcu} is strictly {mcu_voltage}V (non-5V tolerant).",
                    "recommendation": f"Insert a bidirectional logic level shifter (e.g. TXS0108E / 2N7000 FET) between {host_mcu} and {comp}.",
                })

    # 3. Check Current / Power Load
    if host_mcu and total_current_ma > 300:
        compatibility_warnings.append({
            "type": "High Total Current Draw",
            "severity": "NOTICE",
            "details": f"Total peripheral current is {total_current_ma:.1f} mA, exceeding onboard MCU regulator limits.",
            "recommendation": "Use an external dedicated 3.3V/5V buck regulator (e.g. MP1584 / LM7805) to power peripherals.",
        })

    return {
        "status": "issues_detected" if (critical_errors or compatibility_warnings) else "pass",
        "host_mcu": host_mcu,
        "total_estimated_current_ma": round(total_current_ma, 1),
        "i2c_bus_allocation": i2c_bus_allocation,
        "critical_errors": critical_errors,
        "compatibility_warnings": compatibility_warnings,
    }
