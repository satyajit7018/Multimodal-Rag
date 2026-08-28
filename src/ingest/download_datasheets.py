"""Large-Scale Corpus Generator: 32 Industrial Component Datasheets.
Generates comprehensive PDF datasheets across 6 electronics families:
1. Microcontrollers & Wireless (ESP32, RP2040, STM32F103, ATmega328P, nRF52840, ESP8266)
2. Sensors & Converters (BME280, DHT22, MPU6050, VL53L0X, DS18B20, INA219)
3. Power Regulators & PMICs (LM7805, LM317, AMS1117-3.3, TP4056, MP1584, XL6009)
4. Motor Drivers & Actuators (L298N, TB6612FNG, A4988, DRV8833, ULN2003A)
5. Signal Conditioning & Op-Amps (LM358, NE555, LM393, ADS1115, AD620)
6. Communication & Interfaces (MAX485, MCP2515, PCA9685, CH340G)
"""

from __future__ import annotations
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from PIL import Image, ImageDraw

RAW_PDF_DIR = "data/raw_pdfs"
EXTRACTED_IMG_DIR = "data/extracted/images"

DATASHEETS_META = {
    # ---------------- 1. MICROCONTROLLERS & WIRELESS ----------------
    "esp32_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "ESP32 Series Datasheet — 2.4 GHz Wi-Fi and Bluetooth SoC",
        "voltage": "3.3V",
        "i2c_addr": None,
        "description": "ESP32 is a dual-core 32-bit Xtensa LX6 SoC operating up to 240 MHz with integrated 2.4 GHz Wi-Fi (802.11 b/g/n) and Bluetooth v4.2 BR/EDR and BLE. Features 520 KB SRAM, 4-16 MB SPI Flash, capacitive touch, Hall sensor, UART, SPI, I2C, and PWM.",
        "table_title": "Table 1: Operating Conditions & Absolute Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "3.0", "3.3", "3.6", "V"],
            ["Operating Temp", "TOPR", "-40", "25", "125", "°C"],
            ["Max GPIO Current", "I_MAX", "-", "-", "40", "mA"],
            ["Flash Size", "FLASH", "4", "8", "16", "MB"],
            ["SRAM Capacity", "SRAM", "-", "520", "-", "kB"],
        ],
        "diagram_title": "Figure 1: ESP32-WROOM-32 Pinout & Strapping Pins",
        "pins": [("GPIO0 (Boot Pin 25)", 115), ("GPIO2 (LED)", 90), ("TXD0 / RXD0", 65), ("EN (Enable)", 40)],
    },
    "rp2040_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "Raspberry Pi RP2040 Microcontroller Datasheet",
        "voltage": "3.3V",
        "i2c_addr": None,
        "description": "RP2040 is a dual ARM Cortex-M0+ microcontroller designed by Raspberry Pi, running up to 133 MHz. Features 264 KB SRAM in six banks, Programmable I/O (PIO) blocks, dual UART, dual SPI, dual I2C, and 16 PWM channels. IO voltage is 3.3V (non-5V tolerant).",
        "table_title": "Table 1: Electrical Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["IO Supply (IOVDD)", "IOVDD", "1.8", "3.3", "3.63", "V"],
            ["Core Supply (DVDD)", "DVDD", "0.99", "1.10", "1.21", "V"],
            ["Max Clock Freq", "f_MAX", "-", "125", "133", "MHz"],
            ["Total SRAM", "SRAM", "-", "264", "-", "kB"],
            ["PIO State Machines", "PIO_SM", "-", "8", "-", "Units"],
        ],
        "diagram_title": "Figure 1: RP2040 QFN-56 Pin Configuration",
        "pins": [("GPIO0 (I2C0 SDA)", 115), ("GPIO1 (I2C0 SCL)", 90), ("SWCLK / SWDIO", 65), ("RUN (Reset)", 40)],
    },
    "stm32f103_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "STM32F103C8T6 ARM Cortex-M3 32-bit MCU Datasheet",
        "voltage": "3.3V (5V Tolerant on FT pins)",
        "i2c_addr": None,
        "description": "STM32F103xx medium-density performance line incorporates the ARM Cortex-M3 32-bit RISC core operating at 72 MHz, 64-128 KB Flash, 20 KB SRAM, dual 12-bit ADCs, motor control PWM timers, and 5V-tolerant I/O pins.",
        "table_title": "Table 1: General Operating Conditions",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Standard Supply", "VDD", "2.0", "3.3", "3.6", "V"],
            ["CPU Frequency", "f_CPU", "-", "72.0", "72.0", "MHz"],
            ["Flash Memory", "FLASH", "64", "-", "128", "KB"],
            ["SRAM Capacity", "SRAM", "-", "20", "-", "KB"],
            ["Operating Temp", "TA", "-40", "25", "85", "°C"],
        ],
        "diagram_title": "Figure 1: STM32F103 LQFP48 Pinout",
        "pins": [("PA9 (USART1 TX)", 115), ("PA10 (USART1 RX)", 90), ("PB6 (I2C1 SCL)", 65), ("PB7 (I2C1 SDA)", 40)],
    },
    "atmega328p_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "ATmega328P 8-bit AVR Microcontroller Datasheet",
        "voltage": "5.0V (1.8V-5.5V)",
        "i2c_addr": None,
        "description": "The high-performance Microchip 8-bit AVR RISC-based microcontroller combines 32 KB ISP Flash memory with read-while-write capabilities, 1 KB EEPROM, 2 KB SRAM, 23 general-purpose I/O lines, 32 general-purpose working registers, and operates up to 20 MHz at 5V.",
        "table_title": "Table 1: Absolute Maximum Ratings & Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Operating Voltage", "VCC", "1.8", "5.0", "5.5", "V"],
            ["Max Clock Speed", "f_CLK", "-", "16", "20", "MHz"],
            ["DC Current per I/O", "I_IO", "-", "-", "40", "mA"],
            ["Flash Memory", "FLASH", "-", "32", "-", "KB"],
            ["EEPROM", "EEPROM", "-", "1024", "-", "Bytes"],
        ],
        "diagram_title": "Figure 1: ATmega328P 28-Pin DIP Pinout",
        "pins": [("Pin 4 (PD2 / INT0)", 115), ("Pin 27 (PC4 / SDA)", 90), ("Pin 28 (PC5 / SCL)", 65), ("Pin 1 (RESET)", 40)],
    },
    "nrf52840_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "nRF52840 Multiprotocol Bluetooth 5.3 / 802.15.4 SoC Datasheet",
        "voltage": "1.7V-5.5V",
        "i2c_addr": None,
        "description": "Nordic nRF52840 is an advanced ultra-low power multiprotocol SoC with ARM Cortex-M4 with FPU @ 64 MHz, 1 MB Flash, 256 KB RAM, USB 2.0 full speed, high-speed 32 MHz SPI, and integrated 2.4 GHz transceiver supporting BLE 5, Thread, and Zigbee.",
        "table_title": "Table 1: Key Electrical Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Range (VDD)", "VDD", "1.7", "3.0", "3.6", "V"],
            ["High Voltage (VDDH)", "VDDH", "2.5", "5.0", "5.5", "V"],
            ["Radio TX Power", "P_TX", "-20", "+4", "+8", "dBm"],
            ["Flash Memory", "FLASH", "-", "1024", "-", "KB"],
            ["RAM Size", "RAM", "-", "256", "-", "KB"],
        ],
        "diagram_title": "Figure 1: nRF52840 aQFN73 Pinout",
        "pins": [("P0.06 (TXD)", 115), ("P0.08 (RXD)", 90), ("P0.26 (SDA)", 65), ("P0.27 (SCL)", 40)],
    },
    "esp8266_datasheet.pdf": {
        "family": "Microcontrollers & Wireless",
        "title": "ESP8266EX Wi-Fi Microcontroller SoC Datasheet",
        "voltage": "3.3V (2.5V-3.6V)",
        "i2c_addr": None,
        "description": "ESP8266EX delivers a complete and self-contained Wi-Fi networking solution. Powered by Tensilica L106 32-bit RISC core running at 80/160 MHz. Strictly 3.3V operating voltage; non-5V tolerant.",
        "table_title": "Table 1: Operating Conditions",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Operating Voltage", "VDD", "2.5", "3.3", "3.6", "V"],
            ["Max TX Power 802.11b", "P_OUT", "19", "20", "20.5", "dBm"],
            ["Max GPIO Current", "I_MAX", "-", "-", "12", "mA"],
            ["Operating Temp", "TOPR", "-40", "25", "125", "°C"],
        ],
        "diagram_title": "Figure 1: ESP-12E Module Pinout",
        "pins": [("GPIO0 (Flash Mode)", 115), ("GPIO2 (Boot)", 90), ("TXD0 / RXD0", 65), ("CH_PD (Enable)", 40)],
    },

    # ---------------- 2. SENSORS & CONVERTERS ----------------
    "bme280_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "BME280 Combined Humidity, Pressure and Temperature Sensor",
        "voltage": "1.71V-3.6V",
        "i2c_addr": "0x76 (SDO=GND) or 0x77 (SDO=VDD)",
        "description": "Bosch BME280 is an integrated environmental sensor combining relative humidity, barometric pressure and ambient temperature. Features fast response time and high accuracy over I2C and SPI interfaces.",
        "table_title": "Table 1: Operating Conditions & Accuracies",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "1.71", "3.3", "3.6", "V"],
            ["Humidity Tolerance", "A_H", "-", "±3.0", "-", "%RH"],
            ["Pressure Range", "P", "300", "-", "1100", "hPa"],
            ["Temp Accuracy", "A_T", "-", "±0.5", "±1.0", "°C"],
        ],
        "diagram_title": "Figure 1: BME280 LGA-8 Pinout & Bus Connections",
        "pins": [("1: GND", 115), ("2: CSB (Chip Select)", 90), ("3: SDI (SDA)", 65), ("4: SCK (SCL)", 40)],
    },
    "dht22_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "DHT22 (AM2302) Digital Temperature & Humidity Sensor",
        "voltage": "3.3V-6.0V",
        "i2c_addr": None,
        "description": "DHT22 provides calibrated single-bus digital output with capacitive humidity sensing and NTC thermistor temperature measurement.",
        "table_title": "Table 1: Technical Specifications",
        "table_data": [
            ["Specification", "Condition", "Min", "Typ", "Max", "Unit"],
            ["Power Supply", "VDD", "3.3", "5.0", "6.0", "V"],
            ["Temp Range", "-", "-40", "-", "80", "°C"],
            ["Temp Accuracy", "25°C", "-", "±0.5", "-", "°C"],
            ["Humidity Range", "-", "0", "-", "100", "%RH"],
        ],
        "diagram_title": "Figure 1: DHT22 4-Pin Package Pinout Diagram",
        "pins": [("Pin 1: VDD", 115), ("Pin 2: DATA", 90), ("Pin 3: NULL", 65), ("Pin 4: GND", 40)],
    },
    "mpu6050_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "MPU-6050 Six-Axis (Gyro + Accelerometer) MEMS MotionTracking SoC",
        "voltage": "2.375V-3.46V (VDD)",
        "i2c_addr": "0x68 (AD0=GND) or 0x69 (AD0=VCC)",
        "description": "InvenSense MPU-6050 combines a 3-axis gyroscope and a 3-axis accelerometer on the same silicon die, together with an onboard Digital Motion Processor (DMP) capable of processing complex 6-axis MotionFusion algorithms over I2C.",
        "table_title": "Table 1: Operating Conditions & Range Select",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "2.375", "3.3", "3.46", "V"],
            ["Gyro Full-Scale Range", "FS_G", "±250", "-", "±2000", "°/s"],
            ["Accel Full-Scale Range", "FS_A", "±2", "-", "±16", "g"],
            ["I2C Speed", "f_I2C", "-", "400", "400", "kHz"],
        ],
        "diagram_title": "Figure 1: MPU-6050 QFN-24 Pinout Diagram",
        "pins": [("Pin 23: SCL", 115), ("Pin 24: SDA", 90), ("Pin 9: AD0 (Address)", 65), ("Pin 12: INT (Interrupt)", 40)],
    },
    "vl53l0x_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "VL53L0X Time-of-Flight (ToF) Laser-Ranging Distance Sensor",
        "voltage": "2.6V-3.5V",
        "i2c_addr": "0x29 (Default 7-bit)",
        "description": "ST VL53L0X is a Time-of-Flight ranging sensor based on ST's FlightSense technology. Uses 940nm VCSEL emitter to measure absolute distance up to 2m regardless of target reflectance.",
        "table_title": "Table 1: Optical Ranging Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "AVDD", "2.6", "2.8", "3.5", "V"],
            ["Ranging Distance (Indoor)", "DIST", "50", "-", "2000", "mm"],
            ["Ranging Accuracy", "ACC", "-", "±3%", "±5%", "mm"],
            ["I2C Default Address", "ADDR", "-", "0x29", "-", "Hex"],
        ],
        "diagram_title": "Figure 1: VL53L0X LGA-12 Pinout",
        "pins": [("Pin 1: SDA", 115), ("Pin 2: SCL", 90), ("Pin 5: XSHUT (Shutdown)", 65), ("Pin 7: GPIO1 (Interrupt)", 40)],
    },
    "ds18b20_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "DS18B20 Programmable Resolution 1-Wire Digital Thermometer",
        "voltage": "3.0V-5.5V (Parasite power option)",
        "i2c_addr": None,
        "description": "Maxim DS18B20 digital thermometer provides 9-bit to 12-bit Celsius temperature measurements and has an alarm function with nonvolatile user-programmable upper and lower trigger points over a single 1-Wire bus.",
        "table_title": "Table 1: DC Electrical Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage Range", "VDD", "3.0", "5.0", "5.5", "V"],
            ["Thermometer Range", "T_RANGE", "-55", "-", "+125", "°C"],
            ["Thermometer Error", "T_ERR", "-", "±0.5", "±2.0", "°C"],
            ["Conversion Time (12-bit)", "t_CONV", "-", "-", "750", "ms"],
        ],
        "diagram_title": "Figure 1: DS18B20 TO-92 Pin Configuration",
        "pins": [("Pin 1: GND", 115), ("Pin 2: DQ (1-Wire Data)", 90), ("Pin 3: VDD (Power)", 65), ("Pull-up: 4.7 kOhm", 40)],
    },
    "ina219_datasheet.pdf": {
        "family": "Sensors & Converters",
        "title": "INA219 Zero-Drift, Bidirectional Current/Power Monitor with I2C",
        "voltage": "3.0V-5.5V",
        "i2c_addr": "0x40 (A0=GND, A1=GND) up to 0x4F (16 programmable addresses)",
        "description": "TI INA219 is a high-side current shunt and power monitor with an I2C or SMBUS-compatible interface. Monitors shunt voltage drop and bus supply voltage with 12-bit resolution.",
        "table_title": "Table 1: Measurement Limits & Specs",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "Vs", "3.0", "3.3/5.0", "5.5", "V"],
            ["Bus Voltage Range", "V_BUS", "0", "-", "26", "V"],
            ["Max Shunt Voltage", "V_SHUNT", "-", "-", "±320", "mV"],
            ["Gain Error", "GE", "-", "±0.2", "±1.0", "%"],
        ],
        "diagram_title": "Figure 1: INA219 SOT23-8 Pinout & Shunt Wiring",
        "pins": [("Pin 1: IN+ (Shunt)", 115), ("Pin 2: IN- (Shunt)", 90), ("Pin 5: SCL (I2C)", 65), ("Pin 6: SDA (I2C)", 40)],
    },

    # ---------------- 3. POWER REGULATORS & PMICS ----------------
    "lm7805_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "LM7805 3-Terminal Positive 5V Voltage Regulator",
        "voltage": "5V Output (7V-25V Input)",
        "i2c_addr": None,
        "description": "LM7805 is a 3-terminal positive fixed linear voltage regulator providing a 5.0V output with 1.5A max load current. Internal thermal overload and short-circuit current limiting.",
        "table_title": "Table 1: Electrical Characteristics",
        "table_data": [
            ["Characteristic", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Voltage Range", "Vin", "7.0", "10.0", "25.0", "V"],
            ["Output Voltage", "Vo", "4.8", "5.0", "5.2", "V"],
            ["Max Output Current", "Io", "1.0", "1.5", "2.2", "A"],
            ["Dropout Voltage", "Vd", "-", "2.0", "2.5", "V"],
        ],
        "diagram_title": "Figure 1: LM7805 TO-220 Pinout Diagram",
        "pins": [("Pin 1: INPUT (7-25V)", 115), ("Pin 2: GROUND (GND)", 90), ("Pin 3: OUTPUT (5V)", 65), ("Cin=0.33uF, Cout=0.1uF", 40)],
    },
    "lm317_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "LM317 3-Terminal Adjustable Positive Linear Regulator",
        "voltage": "1.25V to 37V Output",
        "i2c_addr": None,
        "description": "LM317 is an adjustable 3-terminal positive-voltage regulator capable of supplying more than 1.5 A over an output-voltage range of 1.25 V to 37 V using only two external resistors.",
        "table_title": "Table 1: Electrical Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Output Voltage Range", "Vout", "1.25", "-", "37.0", "V"],
            ["Reference Voltage", "Vref", "1.20", "1.25", "1.30", "V"],
            ["Max Output Current", "Imax", "1.5", "2.2", "-", "A"],
            ["Line Regulation", "Reg_line", "-", "0.01", "0.04", "%/V"],
        ],
        "diagram_title": "Figure 1: LM317 TO-220 Pinout & Resistor Divider",
        "pins": [("Pin 1: ADJUST (Adj)", 115), ("Pin 2: OUTPUT (Vout)", 90), ("Pin 3: INPUT (Vin)", 65), ("R1=240 Ohm, R2=Adj", 40)],
    },
    "ams1117_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "AMS1117-3.3 1A Low Dropout (LDO) Positive Voltage Regulator",
        "voltage": "3.3V Output (4.75V-12V Input)",
        "i2c_addr": None,
        "description": "AMS1117-3.3 is a low dropout voltage regulator with a dropout voltage of 1.1V at 1A load current. Widely used on microcontroller development boards for 3.3V power rails.",
        "table_title": "Table 1: Electrical Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Voltage Max", "Vin_max", "-", "-", "12.0", "V"],
            ["Output Voltage", "Vout", "3.267", "3.300", "3.333", "V"],
            ["Dropout Voltage (1A)", "V_DO", "-", "1.1", "1.3", "V"],
            ["Current Limit", "I_LIMIT", "1.0", "1.5", "-", "A"],
        ],
        "diagram_title": "Figure 1: AMS1117 SOT-223 Pinout",
        "pins": [("Pin 1: GND / ADJ", 115), ("Pin 2: VOUT (Tab)", 90), ("Pin 3: VIN (Input)", 65), ("Cout=22uF Tantalum", 40)],
    },
    "tp4056_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "TP4056 1A Standalone Linear Li-Ion Battery Charger with Thermal Regulation",
        "voltage": "4.2V Constant-Voltage Charge",
        "i2c_addr": None,
        "description": "TP4056 is a complete constant-current/constant-voltage linear charger for single cell lithium-ion batteries. Charge current programmable up to 1000mA via external resistor RPROG.",
        "table_title": "Table 1: Charging Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Supply Voltage", "VCC", "4.0", "5.0", "8.0", "V"],
            ["Regulated Float Voltage", "VFLOAT", "4.158", "4.200", "4.242", "V"],
            ["Programmable Current", "IBAT", "100", "1000", "1000", "mA"],
            ["Trickle Charge Threshold", "VTRIKL", "2.8", "2.9", "3.0", "V"],
        ],
        "diagram_title": "Figure 1: TP4056 SOP-8 Pinout & Status LEDs",
        "pins": [("Pin 5: BAT (+LiPo)", 115), ("Pin 6: /STDBY (Green)", 90), ("Pin 7: /CHRG (Red)", 65), ("Pin 2: PROG (R_prog)", 40)],
    },
    "mp1584_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "MP1584 3A, 1.5MHz, 28V Step-Down (Buck) Switching Regulator",
        "voltage": "0.8V to 25V Output (4.5V-28V Input)",
        "i2c_addr": None,
        "description": "Monolithic step-down switching regulator with built-in high-side power MOSFET. Achieves 3A continuous output current over wide 4.5V to 28V input range with 92% efficiency.",
        "table_title": "Table 1: Switching Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Voltage Range", "VIN", "4.5", "-", "28.0", "V"],
            ["Continuous Output Current", "IOUT", "-", "-", "3.0", "A"],
            ["Switching Frequency", "f_SW", "100", "1500", "1500", "kHz"],
            ["Feedback Voltage", "V_FB", "0.784", "0.800", "0.816", "V"],
        ],
        "diagram_title": "Figure 1: MP1584 SOIC-8 Pinout & Inductor Loop",
        "pins": [("Pin 1: SW (Switch)", 115), ("Pin 2: EN (Enable)", 90), ("Pin 7: VIN (Power)", 65), ("Pin 8: FB (Feedback)", 40)],
    },
    "xl6009_datasheet.pdf": {
        "family": "Power Management & Regulators",
        "title": "XL6009 400kHz 60V 4A Switching Current Boost (Step-Up) Converter",
        "voltage": "5V to 35V Output (3.0V-32V Input)",
        "i2c_addr": None,
        "description": "Wide input range step-up (boost) DC-DC converter capable of generating output voltages from 5V to 35V with built-in 4A N-channel power MOSFET and 400kHz switching oscillator.",
        "table_title": "Table 1: Boost Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Voltage Range", "VIN", "3.0", "-", "32.0", "V"],
            ["Max Output Voltage", "VOUT", "-", "-", "35.0", "V"],
            ["Switch Current Limit", "I_SW", "-", "4.0", "4.5", "A"],
            ["Oscillator Frequency", "f_OSC", "320", "400", "480", "kHz"],
        ],
        "diagram_title": "Figure 1: XL6009 TO-263 Pinout Diagram",
        "pins": [("Pin 1: GND", 115), ("Pin 2: EN", 90), ("Pin 3: SW (Drain)", 65), ("Pin 4: VIN", 40)],
    },

    # ---------------- 4. MOTOR DRIVERS & ACTUATORS ----------------
    "l298n_datasheet.pdf": {
        "family": "Motor Drivers & Actuators",
        "title": "L298N Dual Full-Bridge (H-Bridge) Motor Driver",
        "voltage": "46V Max Power Stage, 5V Logic",
        "i2c_addr": None,
        "description": "High-voltage, high-current dual full-bridge driver designed to accept standard TTL logic levels and drive inductive loads such as relays, solenoids, DC and stepping motors.",
        "table_title": "Table 1: Absolute Maximum Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (Vs)", "Vs", "-", "-", "46.0", "V"],
            ["Logic Supply (Vss)", "Vss", "4.5", "5.0", "7.0", "V"],
            ["Continuous Current / Bridge", "Io", "-", "2.0", "2.5", "A"],
            ["Total Quiescent Current", "Iq", "-", "24", "40", "mA"],
        ],
        "diagram_title": "Figure 1: L298N Multiwatt-15 Pinout",
        "pins": [("Pin 2: OUT1", 115), ("Pin 3: OUT2", 90), ("Pin 13: OUT3", 65), ("Pin 14: OUT4", 40)],
    },
    "tb6612fng_datasheet.pdf": {
        "family": "Motor Drivers & Actuators",
        "title": "TB6612FNG Dual DC Motor Driver IC with MOSFET Output",
        "voltage": "2.5V-13.5V Motor, 2.7V-5.5V Logic",
        "i2c_addr": None,
        "description": "Toshiba TB6612FNG features low-RDS(on) DMOS output transistors delivering higher efficiency and lower heat dissipation than bipolar L298N drivers. Output 1.2A continuous (3.2A peak).",
        "table_title": "Table 1: Operating Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Motor Supply (VM)", "VM", "2.5", "-", "13.5", "V"],
            ["Logic Supply (VCC)", "VCC", "2.7", "3.3/5.0", "5.5", "V"],
            ["Continuous Current", "IOUT", "-", "1.2", "-", "A"],
            ["MOSFET On-Resistance", "Ron", "-", "0.5", "0.7", "Ohm"],
        ],
        "diagram_title": "Figure 1: TB6612FNG SSOP24 Pinout",
        "pins": [("Pin 1: AO1", 115), ("Pin 2: AO2", 90), ("Pin 19: PWMA", 65), ("Pin 21: STBY (Standby)", 40)],
    },
    "a4988_datasheet.pdf": {
        "family": "Motor Drivers & Actuators",
        "title": "A4988 DMOS Microstepping Stepper Motor Driver with Translator",
        "voltage": "8V-35V Motor Supply, 3.0V-5.5V Logic",
        "i2c_addr": None,
        "description": "Allegro A4988 is a complete microstepping motor driver with built-in translator for easy operation. Operates bipolar stepper motors in full, half, 1/4, 1/8, and 1/16-step modes with internal PWM current control.",
        "table_title": "Table 1: Stepper Ratings & Step Resolution",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Motor Load Supply", "VBB", "8.0", "-", "35.0", "V"],
            ["Logic Supply Voltage", "VDD", "3.0", "5.0", "5.5", "V"],
            ["Max Continuous Current", "IOUT", "-", "-", "2.0", "A"],
            ["Microstep Modes (MS1-MS3)", "STEPS", "Full", "-", "1/16", "Step"],
        ],
        "diagram_title": "Figure 1: A4988 QFN-28 Module Pinout",
        "pins": [("STEP (Pulse)", 115), ("DIR (Direction)", 90), ("MS1 / MS2 / MS3", 65), ("1A / 1B / 2A / 2B", 40)],
    },
    "drv8833_datasheet.pdf": {
        "family": "Motor Drivers & Actuators",
        "title": "DRV8833 Dual H-Bridge Low-Voltage Motor Driver",
        "voltage": "2.7V-10.8V Motor Supply",
        "i2c_addr": None,
        "description": "TI DRV8833 provides dual H-bridge motor driver solution for toys, printers, and low-voltage robotics. Operates from 2.7V to 10.8V with 1.5A RMS current per bridge.",
        "table_title": "Table 1: Electrical Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Power Supply Voltage", "VM", "2.7", "-", "10.8", "V"],
            ["Max Output Current (RMS)", "I_RMS", "-", "1.5", "2.0", "A"],
            ["MOSFET RDS(on) Total", "RDS", "-", "360", "450", "mOhm"],
            ["Sleep Current", "I_SLEEP", "-", "1.6", "3.0", "uA"],
        ],
        "diagram_title": "Figure 1: DRV8833 HTSSOP-16 Pinout",
        "pins": [("Pin 2: AOUT1", 115), ("Pin 4: AOUT2", 90), ("Pin 9: AIN1", 65), ("Pin 10: AIN2", 40)],
    },
    "uln2003a_datasheet.pdf": {
        "family": "Motor Drivers & Actuators",
        "title": "ULN2003A High-Voltage High-Current 7-Channel Darlington Transistor Array",
        "voltage": "50V Max Output Collector Voltage",
        "i2c_addr": None,
        "description": "ULN2003A consists of seven NPN Darlington pairs that feature high-voltage outputs with common-cathode clamp diodes for switching inductive loads such as unipolar stepper motors and 5V relays.",
        "table_title": "Table 1: Absolute Maximum Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Collector-Emitter Voltage", "VCE", "-", "-", "50.0", "V"],
            ["Continuous Collector Current", "IC", "-", "-", "500", "mA"],
            ["Base Input Resistor", "RIN", "-", "2.7", "-", "kOhm"],
            ["DC Current Gain", "hFE", "1000", "-", "-", "-"],
        ],
        "diagram_title": "Figure 1: ULN2003A 16-Pin DIP Pinout",
        "pins": [("Pin 1: 1B (Input 1)", 115), ("Pin 16: 1C (Output 1)", 90), ("Pin 8: GND (Emitter)", 65), ("Pin 9: COM (Flyback)", 40)],
    },

    # ---------------- 5. SIGNAL CONDITIONING & OP-AMPS ----------------
    "lm358_datasheet.pdf": {
        "family": "Signal Conditioning & Op-Amps",
        "title": "LM358 Dual Low-Power Operational Amplifier",
        "voltage": "3.0V-32V Single, ±1.5V-±16V Dual",
        "i2c_addr": None,
        "description": "Two independent, high-gain, internally frequency-compensated operational amplifiers designed specifically to operate from a single power supply over a wide range of voltages.",
        "table_title": "Table 1: Electrical Specifications",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (Single)", "VCC", "3.0", "-", "32.0", "V"],
            ["Supply Voltage (Dual)", "VCC/VEE", "±1.5", "-", "±16.0", "V"],
            ["Input Offset Voltage", "Vio", "-", "2.0", "7.0", "mV"],
            ["Large Signal Voltage Gain", "Avd", "25", "100", "-", "V/mV"],
        ],
        "diagram_title": "Figure 1: LM358 8-Pin DIP Pin Configuration",
        "pins": [("1: 1OUT", 115), ("2: 1IN- (Inv)", 90), ("3: 1IN+ (Non-Inv)", 65), ("4: GND, 8: VCC", 40)],
    },
    "ne555_datasheet.pdf": {
        "family": "Signal Conditioning & Op-Amps",
        "title": "NE555 Precision Timer IC Datasheet",
        "voltage": "4.5V-16V Operating Supply",
        "i2c_addr": None,
        "description": "Precision timing circuit capable of producing accurate time delays or oscillation in monostable or astable multivibrator modes.",
        "table_title": "Table 1: Electrical Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VCC", "4.5", "5.0", "16.0", "V"],
            ["Max Sink/Source Current", "Iout", "-", "-", "200", "mA"],
            ["Timing Error (Monostable)", "TERR", "-", "1.0", "3.0", "%"],
            ["Threshold Voltage", "Vth", "-", "2/3 VCC", "-", "V"],
        ],
        "diagram_title": "Figure 1: NE555 8-Pin DIP Pinout",
        "pins": [("Pin 2: TRIG (Trigger)", 115), ("Pin 3: OUT (Output)", 90), ("Pin 7: DISCH (Discharge)", 65), ("Pin 4: RESET", 40)],
    },
    "lm393_datasheet.pdf": {
        "family": "Signal Conditioning & Op-Amps",
        "title": "LM393 Dual Differential Comparator with Open-Collector Output",
        "voltage": "2.0V-36V Single, ±1.0V-±18V Dual",
        "i2c_addr": None,
        "description": "Consists of two independent precision voltage comparators designed to operate from a single power supply over a wide voltage range. Features open-collector outputs compatible with TTL, DTL, and CMOS.",
        "table_title": "Table 1: Comparator Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage Range", "VCC", "2.0", "5.0", "36.0", "V"],
            ["Input Offset Voltage", "VIO", "-", "1.0", "5.0", "mV"],
            ["Response Time", "t_RES", "-", "1.3", "2.5", "us"],
            ["Output Sink Current", "I_SINK", "6", "16", "-", "mA"],
        ],
        "diagram_title": "Figure 1: LM393 8-Pin DIP Pinout & Pull-up Resistor",
        "pins": [("Pin 1: 1OUT (Open Coll)", 115), ("Pin 2: 1IN-", 90), ("Pin 3: 1IN+", 65), ("Requires Pull-Up Resistor", 40)],
    },
    "ads1115_datasheet.pdf": {
        "family": "Signal Conditioning & Op-Amps",
        "title": "ADS1115 16-Bit Ultra-Small ADC with Internal Reference and Oscillator",
        "voltage": "2.0V-5.5V Supply",
        "i2c_addr": "0x48 (ADDR=GND), 0x49 (ADDR=VDD), 0x4A (ADDR=SDA), 0x4B (ADDR=SCL)",
        "description": "TI ADS1115 provides 16 bits of precision at 860 samples/second over I2C. Includes programmable gain amplifier (PGA), internal voltage reference, and four single-ended or two differential input channels.",
        "table_title": "Table 1: ADC Specifications & Gain Ranges",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "2.0", "3.3/5.0", "5.5", "V"],
            ["Full-Scale Input Range", "FSR", "±0.256", "-", "±6.144", "V"],
            ["Data Rate", "DR", "8", "-", "860", "SPS"],
            ["Differential Linearity", "DNL", "-", "±0.5", "-", "LSB"],
        ],
        "diagram_title": "Figure 1: ADS1115 MSOP-10 Pinout Diagram",
        "pins": [("Pin 4: AIN0", 115), ("Pin 5: AIN1", 90), ("Pin 9: SCL (I2C)", 65), ("Pin 10: SDA (I2C)", 40)],
    },
    "ad620_datasheet.pdf": {
        "family": "Signal Conditioning & Op-Amps",
        "title": "AD620 Low-Cost, Low-Power Instrumentation Amplifier",
        "voltage": "±2.3V to ±18V Dual Power Supply",
        "i2c_addr": None,
        "description": "Analog Devices AD620 is a complete, high accuracy instrumentation amplifier with gain set from 1 to 10,000 using only a single external resistor RG: Gain = 1 + (49.4 kOhm / RG).",
        "table_title": "Table 1: Gain & Precision Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Range", "Vs", "±2.3", "±15.0", "±18.0", "V"],
            ["Gain Range", "G", "1", "-", "10000", "V/V"],
            ["CMRR (G=10)", "CMRR", "93", "100", "-", "dB"],
            ["Input Offset Voltage", "VOSI", "-", "30", "125", "uV"],
        ],
        "diagram_title": "Figure 1: AD620 8-Pin DIP Pinout & RG Gain Resistor",
        "pins": [("Pin 1: RG (Gain Pin)", 115), ("Pin 8: RG (Gain Pin)", 90), ("Pin 2: -IN (Inv Input)", 65), ("Pin 3: +IN (Non-Inv Input)", 40)],
    },

    # ---------------- 6. COMMUNICATION & INTERFACES ----------------
    "max485_datasheet.pdf": {
        "family": "Communication & Interfaces",
        "title": "MAX485 Low-Power RS-485/RS-422 Transceiver",
        "voltage": "4.75V-5.25V (5V Nominal)",
        "i2c_addr": None,
        "description": "MAX485 is a high-speed transceiver for RS-485 and RS-422 differential communication operating up to 2.5 Mbps with half-duplex operation.",
        "table_title": "Table 1: DC Electrical Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VCC", "4.75", "5.00", "5.25", "V"],
            ["Max Data Rate", "DR", "2.5", "-", "-", "Mbps"],
            ["Driver Differential Output", "Vod", "1.5", "-", "5.0", "V"],
            ["Quiescent Current", "Icc", "-", "300", "500", "uA"],
        ],
        "diagram_title": "Figure 1: MAX485 8-Pin DIP Pin Configuration",
        "pins": [("Pin 1: RO (Receiver Out)", 115), ("Pin 4: DI (Driver In)", 90), ("Pin 6: A (Non-Inverting)", 65), ("Pin 7: B (Inverting)", 40)],
    },
    "mcp2515_datasheet.pdf": {
        "family": "Communication & Interfaces",
        "title": "MCP2515 Stand-Alone CAN Controller with SPI Interface",
        "voltage": "2.7V-5.5V Supply",
        "i2c_addr": None,
        "description": "Microchip MCP2515 is a stand-alone Controller Area Network (CAN) controller that implements the CAN specification, Version 2.0B. Capable of transmitting and receiving both standard and extended data frames over SPI up to 10 MHz.",
        "table_title": "Table 1: CAN Protocol Specs & SPI Timing",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "2.7", "5.0", "5.5", "V"],
            ["Max SPI Clock Speed", "f_SPI", "-", "-", "10.0", "MHz"],
            ["Max CAN Bit Rate", "f_CAN", "-", "1.0", "1.0", "Mbps"],
            ["Transmit Buffers", "TXB", "-", "3", "-", "Buffers"],
        ],
        "diagram_title": "Figure 1: MCP2515 18-Pin DIP Pinout Diagram",
        "pins": [("Pin 1: TXCAN (To Transceiver)", 115), ("Pin 2: RXCAN", 90), ("Pin 14: SCK (SPI Clock)", 65), ("Pin 16: /CS (Chip Select)", 40)],
    },
    "pca9685_datasheet.pdf": {
        "family": "Communication & Interfaces",
        "title": "PCA9685 16-channel, 12-bit PWM Fm+ I2C-bus LED & Servo Controller",
        "voltage": "2.3V-5.5V Logic Supply",
        "i2c_addr": "0x40 (Default when A0-A5=GND)",
        "description": "16-channel I2C-bus controlled LED and servo controller. Each channel has an independent 12-bit resolution (4096 steps) PWM controller with programmable frequency from 24 Hz to 1526 Hz.",
        "table_title": "Table 1: Static Characteristics",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "2.3", "3.3/5.0", "5.5", "V"],
            ["Default I2C Address", "ADDR", "-", "0x40", "-", "Hex"],
            ["PWM Channels", "CH", "-", "16", "-", "Ch"],
            ["PWM Resolution", "RES", "-", "12", "-", "Bits"],
        ],
        "diagram_title": "Figure 1: PCA9685 TSSOP28 Pinout Diagram",
        "pins": [("Pin 26: SCL (I2C)", 115), ("Pin 27: SDA (I2C)", 90), ("Pin 23: /OE (Output Enable)", 65), ("Pins 6-21: LED0-LED15", 40)],
    },
    "ch340g_datasheet.pdf": {
        "family": "Communication & Interfaces",
        "title": "CH340G USB to Serial UART Bridge Controller Datasheet",
        "voltage": "3.3V or 5.0V Operating Voltage",
        "i2c_addr": None,
        "description": "WCH CH340G is a USB bus adapter chip that provides USB to serial UART, IrDA infrared interface or printer interface. Supports baud rates from 50 bps to 2 Mbps with built-in clock generator.",
        "table_title": "Table 1: Electrical Parameters",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (5V Mode)", "VCC_5", "4.5", "5.0", "5.3", "V"],
            ["Supply Voltage (3.3V Mode)", "VCC_3", "3.0", "3.3", "3.6", "V"],
            ["Max Baud Rate", "BAUD", "50", "-", "2000000", "bps"],
            ["Supply Current", "ICC", "-", "12", "30", "mA"],
        ],
        "diagram_title": "Figure 1: CH340G SOP-16 Pinout Diagram",
        "pins": [("Pin 2: TXD (Transmit)", 115), ("Pin 3: RXD (Receive)", 90), ("Pin 5: UD+ (USB Data+)", 65), ("Pin 6: UD- (USB Data-)", 40)],
    },
}


def draw_pinout_diagram(title: str, pins: list[tuple[str, int]]) -> Drawing:
    """Generates an annotated visual vector diagram for the PDF datasheet."""
    d = Drawing(480, 180)
    d.add(Rect(0, 0, 480, 180, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=1, rx=6, ry=6))
    d.add(String(20, 160, title, fontName="Helvetica-Bold", fontSize=10.5, fillColor=colors.HexColor("#0F172A")))

    # Central IC Body
    d.add(Rect(140, 30, 200, 110, fillColor=colors.HexColor("#1E293B"), strokeColor=colors.HexColor("#475569"), strokeWidth=1.5, rx=4, ry=4))
    d.add(Circle(155, 125, 4, fillColor=colors.HexColor("#94A3B8"), strokeColor=None))  # Pin 1 index dot

    clean_name = title.split(":")[0].replace("Figure 1", "").strip() or "IC"
    d.add(String(190, 80, clean_name[:12], fontName="Helvetica-Bold", fontSize=13, fillColor=colors.white))

    colors_list = [colors.HexColor("#3B82F6"), colors.HexColor("#10B981"), colors.HexColor("#F59E0B"), colors.HexColor("#EC4899")]
    for idx, (label, y) in enumerate(pins[:4]):
        pin_color = colors_list[idx % len(colors_list)]
        d.add(Line(100, y, 140, y, strokeColor=pin_color, strokeWidth=2))
        d.add(String(15, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))

    return d


def create_standalone_crop_image(title: str, pins: list[tuple[str, int]], output_path: str):
    """Generates and saves a PNG crop of the diagram for visual grounding."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (640, 320), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([10, 10, 630, 310], radius=8, outline=(203, 213, 225), width=2)
    draw.text((25, 20), title, fill=(15, 23, 42))

    # IC body
    draw.rounded_rectangle([200, 65, 440, 255], radius=6, fill=(30, 41, 59), outline=(71, 85, 105), width=2)
    draw.ellipse([215, 80, 225, 90], fill=(148, 163, 184))
    draw.text((260, 150), title.split(":")[0][:14], fill=(255, 255, 255))

    # Pins
    colors_rgb = [(59, 130, 246), (16, 185, 129), (245, 158, 11), (236, 72, 153)]
    y_positions = [85, 135, 185, 235]
    for idx, (label, _) in enumerate(pins[:4]):
        y = y_positions[idx]
        col = colors_rgb[idx % len(colors_rgb)]
        draw.line([120, y, 200, y], fill=col, width=3)
        draw.text((20, y - 6), label, fill=(30, 41, 59))

    img.save(output_path)


def generate_all_datasheets():
    """Generates all 32 target datasheets and saves them to data/raw_pdfs/."""
    os.makedirs(RAW_PDF_DIR, exist_ok=True)
    os.makedirs(EXTRACTED_IMG_DIR, exist_ok=True)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )

    for pdf_filename, meta in DATASHEETS_META.items():
        pdf_path = os.path.join(RAW_PDF_DIR, pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        # Page 1: Overview
        story.append(Paragraph(meta["title"], title_style))
        story.append(Paragraph(f"<b>Family: {meta['family']} | Operating Voltage: {meta['voltage']}</b>", body_style))
        story.append(Paragraph("<b>Section 1: General Description & Features</b>", h2_style))
        story.append(Paragraph(meta["description"], body_style))
        story.append(Spacer(1, 10))

        # Page 2: Table
        story.append(PageBreak())
        story.append(Paragraph(f"<b>{meta['table_title']}</b>", h2_style))
        t_data = meta["table_data"]
        table = Table(t_data, colWidths=[140, 70, 60, 60, 60, 60])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(table)
        story.append(Spacer(1, 10))

        # Page 3: Diagram
        story.append(PageBreak())
        story.append(Paragraph(f"<b>{meta['diagram_title']}</b>", h2_style))
        diagram_drawing = draw_pinout_diagram(meta["diagram_title"], meta["pins"])
        story.append(diagram_drawing)
        story.append(Spacer(1, 8))
        story.append(Paragraph("<i>Note: Pin numbers and electrical ratings above must be strictly observed.</i>", body_style))

        doc.build(story)

        crop_name = pdf_filename.replace(".pdf", "_diagram_p3.png")
        crop_path = os.path.join(EXTRACTED_IMG_DIR, crop_name)
        create_standalone_crop_image(meta["diagram_title"], meta["pins"], crop_path)

    print(f"Successfully generated all {len(DATASHEETS_META)} PDF datasheets and diagram crops in {RAW_PDF_DIR}!")


if __name__ == "__main__":
    generate_all_datasheets()
