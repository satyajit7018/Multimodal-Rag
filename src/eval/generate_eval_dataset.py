"""Evaluation Dataset Generator: 105 Curated Questions.
Generates comprehensive benchmark covering:
1. 35 Text questions (Features, architecture, applications)
2. 35 Table questions (Electrical specs, min/max ratings, tolerances)
3. 20 Diagram questions (Pinout configurations, signal wiring)
4. 15 Comparative & Circuit Compatibility questions (Cross-datasheet analysis)
"""

import json
import os

EVAL_SET_PATH = "data/eval_set.json"

QUESTIONS = [
    # ---------------- 1. TEXT QUESTIONS (35) ----------------
    {
        "id": "t1", "category": "text", "source_doc": "esp32_datasheet.pdf", "page": 1,
        "question": "What is the ESP32 typically used for in IoT applications?",
        "answer": "Wi-Fi and Bluetooth enabled dual-core microcontroller for connected IoT edge devices"
    },
    {
        "id": "t2", "category": "text", "source_doc": "esp32_datasheet.pdf", "page": 1,
        "question": "What type of CPU core is used in the ESP32 microcontroller?",
        "answer": "Xtensa dual-core 32-bit LX6 microprocessor"
    },
    {
        "id": "t3", "category": "text", "source_doc": "rp2040_datasheet.pdf", "page": 1,
        "question": "What processor core architecture powers the Raspberry Pi RP2040 microcontroller?",
        "answer": "Dual ARM Cortex-M0+ cores running up to 133 MHz"
    },
    {
        "id": "t4", "category": "text", "source_doc": "rp2040_datasheet.pdf", "page": 1,
        "question": "What unique hardware subsystem in the RP2040 allows custom digital interface emulation?",
        "answer": "Programmable I/O (PIO) state machine blocks"
    },
    {
        "id": "t5", "category": "text", "source_doc": "stm32f103_datasheet.pdf", "page": 1,
        "question": "What processor core is the STM32F103 microcontroller based on?",
        "answer": "ARM Cortex-M3 32-bit RISC core operating up to 72 MHz"
    },
    {
        "id": "t6", "category": "text", "source_doc": "atmega328p_datasheet.pdf", "page": 1,
        "question": "What microcontroller architecture does the ATmega328P belong to?",
        "answer": "8-bit AVR RISC-based microcontroller"
    },
    {
        "id": "t7", "category": "text", "source_doc": "nrf52840_datasheet.pdf", "page": 1,
        "question": "What wireless protocols does the nRF52840 SoC natively support?",
        "answer": "Bluetooth 5.3 Low Energy (BLE), Thread, Zigbee, and proprietary 2.4 GHz protocols"
    },
    {
        "id": "t8", "category": "text", "source_doc": "esp8266_datasheet.pdf", "page": 1,
        "question": "What core processor is used in the ESP8266EX Wi-Fi chip?",
        "answer": "Tensilica L106 32-bit RISC core"
    },
    {
        "id": "t9", "category": "text", "source_doc": "bme280_datasheet.pdf", "page": 1,
        "question": "What three environmental parameters are measured by the BME280 sensor?",
        "answer": "Barometric pressure, ambient temperature, and relative humidity"
    },
    {
        "id": "t10", "category": "text", "source_doc": "bme280_datasheet.pdf", "page": 1,
        "question": "What interface protocols does the BME280 sensor support for host communication?",
        "answer": "I2C and SPI digital communication interfaces"
    },
    {
        "id": "t11", "category": "text", "source_doc": "dht22_datasheet.pdf", "page": 1,
        "question": "What is the DHT22 (AM2302) sensor used for?",
        "answer": "Digital temperature and relative humidity measurement with single-bus digital output"
    },
    {
        "id": "t12", "category": "text", "source_doc": "mpu6050_datasheet.pdf", "page": 1,
        "question": "What internal processing engine does the MPU-6050 integrate for motion fusion?",
        "answer": "Digital Motion Processor (DMP) for onboard 6-axis MotionFusion algorithms"
    },
    {
        "id": "t13", "category": "text", "source_doc": "vl53l0x_datasheet.pdf", "page": 1,
        "question": "What operating principle does the VL53L0X distance sensor use to measure proximity?",
        "answer": "Time-of-Flight (ToF) laser-ranging based on 940nm VCSEL light pulses"
    },
    {
        "id": "t14", "category": "text", "source_doc": "ds18b20_datasheet.pdf", "page": 1,
        "question": "What communication protocol does the DS18B20 digital thermometer use?",
        "answer": "Dallas/Maxim 1-Wire single data line protocol"
    },
    {
        "id": "t15", "category": "text", "source_doc": "ina219_datasheet.pdf", "page": 1,
        "question": "What electrical measurements does the INA219 sensor perform?",
        "answer": "High-side current shunt voltage drop, bus voltage, and calculated power"
    },
    {
        "id": "t16", "category": "text", "source_doc": "lm7805_datasheet.pdf", "page": 1,
        "question": "What is the primary function of the LM7805 integrated circuit?",
        "answer": "3-terminal positive fixed linear voltage regulator providing 5V output"
    },
    {
        "id": "t17", "category": "text", "source_doc": "lm7805_datasheet.pdf", "page": 1,
        "question": "Does the LM7805 include internal thermal overload protection?",
        "answer": "Yes, it includes internal thermal overload protection and short-circuit current limiting"
    },
    {
        "id": "t18", "category": "text", "source_doc": "lm317_datasheet.pdf", "page": 1,
        "question": "How is the output voltage of an LM317 regulator adjusted?",
        "answer": "Using a resistor divider between output, adjust pin, and ground"
    },
    {
        "id": "t19", "category": "text", "source_doc": "ams1117_datasheet.pdf", "page": 1,
        "question": "Why is the AMS1117-3.3 categorized as a Low Dropout (LDO) regulator?",
        "answer": "It requires only 1.1V input-to-output voltage differential at 1A load"
    },
    {
        "id": "t20", "category": "text", "source_doc": "tp4056_datasheet.pdf", "page": 1,
        "question": "What type of battery chemistry is the TP4056 IC designed to charge?",
        "answer": "Single-cell 3.7V/4.2V Lithium-Ion and Lithium-Polymer batteries"
    },
    {
        "id": "t21", "category": "text", "source_doc": "mp1584_datasheet.pdf", "page": 1,
        "question": "What power conversion topology does the MP1584 regulator use?",
        "answer": "Step-down (buck) high-frequency switching regulator"
    },
    {
        "id": "t22", "category": "text", "source_doc": "xl6009_datasheet.pdf", "page": 1,
        "question": "What power conversion topology does the XL6009 IC provide?",
        "answer": "Step-up (boost) switching DC-DC converter"
    },
    {
        "id": "t23", "category": "text", "source_doc": "l298n_datasheet.pdf", "page": 1,
        "question": "What is the L298N IC designed to drive in robotics and automation projects?",
        "answer": "Inductive loads such as DC motors, stepper motors, relays, and solenoids"
    },
    {
        "id": "t24", "category": "text", "source_doc": "l298n_datasheet.pdf", "page": 1,
        "question": "What topology is used in the L298N motor driver output stage?",
        "answer": "Dual full-bridge (H-bridge) driver"
    },
    {
        "id": "t25", "category": "text", "source_doc": "tb6612fng_datasheet.pdf", "page": 1,
        "question": "What semiconductor technology gives TB6612FNG higher efficiency than L298N?",
        "answer": "Low-RDS(on) DMOS/MOSFET output switches resulting in lower heat generation"
    },
    {
        "id": "t26", "category": "text", "source_doc": "a4988_datasheet.pdf", "page": 1,
        "question": "What type of motor is the A4988 integrated circuit specifically designed for?",
        "answer": "Bipolar stepper motors with microstepping translation"
    },
    {
        "id": "t27", "category": "text", "source_doc": "drv8833_datasheet.pdf", "page": 1,
        "question": "What applications is the DRV8833 dual H-bridge motor driver optimized for?",
        "answer": "Low-voltage battery-powered robotics, toys, and printers"
    },
    {
        "id": "t28", "category": "text", "source_doc": "uln2003a_datasheet.pdf", "page": 1,
        "question": "What circuit structure is inside each channel of the ULN2003A driver?",
        "answer": "High-voltage high-current NPN Darlington transistor pair with flyback clamp diode"
    },
    {
        "id": "t29", "category": "text", "source_doc": "lm358_datasheet.pdf", "page": 1,
        "question": "What type of operational amplifier is the LM358?",
        "answer": "Dual low-power operational amplifier designed to operate from a single power supply"
    },
    {
        "id": "t30", "category": "text", "source_doc": "ne555_datasheet.pdf", "page": 1,
        "question": "What is the NE555 precision timer commonly used for?",
        "answer": "Generating accurate time delays or oscillation in astable and monostable modes"
    },
    {
        "id": "t31", "category": "text", "source_doc": "lm393_datasheet.pdf", "page": 1,
        "question": "What output stage structure does the LM393 voltage comparator have?",
        "answer": "Open-collector output requiring an external pull-up resistor"
    },
    {
        "id": "t32", "category": "text", "source_doc": "ads1115_datasheet.pdf", "page": 1,
        "question": "What resolution and sampling rate does the ADS1115 ADC offer?",
        "answer": "16-bit analog-to-digital resolution at up to 860 samples per second"
    },
    {
        "id": "t33", "category": "text", "source_doc": "ad620_datasheet.pdf", "page": 1,
        "question": "How is the amplification gain set on the AD620 instrumentation amplifier?",
        "answer": "With a single external resistor RG between pins 1 and 8"
    },
    {
        "id": "t34", "category": "text", "source_doc": "max485_datasheet.pdf", "page": 1,
        "question": "What bus standard is the MAX485 transceiver designed for?",
        "answer": "RS-485 and RS-422 differential multipoint communication"
    },
    {
        "id": "t35", "category": "text", "source_doc": "mcp2515_datasheet.pdf", "page": 1,
        "question": "What automotive/industrial bus protocol is implemented by the MCP2515 chip?",
        "answer": "Controller Area Network (CAN) protocol Version 2.0B over SPI interface"
    },

    # ---------------- 2. TABLE QUESTIONS (35) ----------------
    {
        "id": "tab1", "category": "table", "source_doc": "lm7805_datasheet.pdf", "page": 2,
        "question": "What is the recommended operating input voltage range for the LM7805 regulator?",
        "answer": "7V to 25V input voltage range"
    },
    {
        "id": "tab2", "category": "table", "source_doc": "lm7805_datasheet.pdf", "page": 2,
        "question": "What is the maximum output current capability of the LM7805 with adequate heatsinking?",
        "answer": "1.5A maximum output current (up to 2.2A peak)"
    },
    {
        "id": "tab3", "category": "table", "source_doc": "lm317_datasheet.pdf", "page": 2,
        "question": "What is the adjustable output voltage range of the LM317 regulator?",
        "answer": "1.25V to 37V output voltage range"
    },
    {
        "id": "tab4", "category": "table", "source_doc": "ams1117_datasheet.pdf", "page": 2,
        "question": "What is the typical dropout voltage of the AMS1117-3.3 regulator at 1A load?",
        "answer": "1.1V typical dropout voltage (1.3V max)"
    },
    {
        "id": "tab5", "category": "table", "source_doc": "tp4056_datasheet.pdf", "page": 2,
        "question": "What is the regulated battery float charging voltage for the TP4056 Li-Ion charger?",
        "answer": "4.200V (4.158V to 4.242V float voltage)"
    },
    {
        "id": "tab6", "category": "table", "source_doc": "mp1584_datasheet.pdf", "page": 2,
        "question": "What is the maximum continuous output current of the MP1584 buck converter?",
        "answer": "3.0A continuous output current"
    },
    {
        "id": "tab7", "category": "table", "source_doc": "mp1584_datasheet.pdf", "page": 2,
        "question": "What is the maximum input voltage rating for the MP1584 step-down regulator?",
        "answer": "28.0V maximum input voltage"
    },
    {
        "id": "tab8", "category": "table", "source_doc": "xl6009_datasheet.pdf", "page": 2,
        "question": "What is the internal switching oscillator frequency of the XL6009 boost converter?",
        "answer": "400 kHz typical switching frequency"
    },
    {
        "id": "tab9", "category": "table", "source_doc": "l298n_datasheet.pdf", "page": 2,
        "question": "What is the absolute maximum supply voltage (Vs) rating for the L298N motor driver power stage?",
        "answer": "46V maximum supply voltage"
    },
    {
        "id": "tab10", "category": "table", "source_doc": "l298n_datasheet.pdf", "page": 2,
        "question": "What is the maximum continuous DC load current per channel for the L298N driver?",
        "answer": "2.0A continuous DC current per bridge (2.5A peak)"
    },
    {
        "id": "tab11", "category": "table", "source_doc": "tb6612fng_datasheet.pdf", "page": 2,
        "question": "What is the motor supply voltage range (VM) for the TB6612FNG driver?",
        "answer": "2.5V to 13.5V motor supply range"
    },
    {
        "id": "tab12", "category": "table", "source_doc": "tb6612fng_datasheet.pdf", "page": 2,
        "question": "What is the typical MOSFET on-resistance (Ron) of the TB6612FNG output switches?",
        "answer": "0.5 Ohm typical on-resistance"
    },
    {
        "id": "tab13", "category": "table", "source_doc": "a4988_datasheet.pdf", "page": 2,
        "question": "What is the motor load supply voltage range for the A4988 stepper driver?",
        "answer": "8.0V to 35.0V motor load supply range"
    },
    {
        "id": "tab14", "category": "table", "source_doc": "a4988_datasheet.pdf", "page": 2,
        "question": "What is the finest microstep resolution available on the A4988 driver?",
        "answer": "1/16 step microstep resolution"
    },
    {
        "id": "tab15", "category": "table", "source_doc": "drv8833_datasheet.pdf", "page": 2,
        "question": "What is the continuous RMS current rating per bridge for the DRV8833 motor driver?",
        "answer": "1.5A RMS current per bridge"
    },
    {
        "id": "tab16", "category": "table", "source_doc": "uln2003a_datasheet.pdf", "page": 2,
        "question": "What is the maximum continuous collector current rating per channel for the ULN2003A?",
        "answer": "500 mA maximum collector current"
    },
    {
        "id": "tab17", "category": "table", "source_doc": "lm358_datasheet.pdf", "page": 2,
        "question": "What is the absolute maximum supply voltage rating for the LM358 dual op-amp in single-supply mode?",
        "answer": "32V maximum supply voltage"
    },
    {
        "id": "tab18", "category": "table", "source_doc": "lm358_datasheet.pdf", "page": 2,
        "question": "What is the typical input offset voltage for the LM358 at 25°C?",
        "answer": "2.0 mV typical input offset voltage (7.0 mV max)"
    },
    {
        "id": "tab19", "category": "table", "source_doc": "ne555_datasheet.pdf", "page": 2,
        "question": "What is the operating supply voltage range for the NE555 timer IC?",
        "answer": "4.5V to 16V operating supply voltage"
    },
    {
        "id": "tab20", "category": "table", "source_doc": "ne555_datasheet.pdf", "page": 2,
        "question": "What is the maximum output source and sink current for the NE555 timer output pin?",
        "answer": "200 mA maximum sink or source current"
    },
    {
        "id": "tab21", "category": "table", "source_doc": "lm393_datasheet.pdf", "page": 2,
        "question": "What is the maximum supply voltage rating for the LM393 voltage comparator?",
        "answer": "36.0V maximum supply voltage"
    },
    {
        "id": "tab22", "category": "table", "source_doc": "ads1115_datasheet.pdf", "page": 2,
        "question": "What is the default full-scale input voltage range (FSR) setting of the ADS1115 ADC?",
        "answer": "±2.048V (with options from ±0.256V up to ±6.144V)"
    },
    {
        "id": "tab23", "category": "table", "source_doc": "ad620_datasheet.pdf", "page": 2,
        "question": "What is the maximum gain capability of the AD620 instrumentation amplifier?",
        "answer": "10,000 V/V maximum gain"
    },
    {
        "id": "tab24", "category": "table", "source_doc": "max485_datasheet.pdf", "page": 2,
        "question": "What is the maximum data transmission rate specified for the MAX485 transceiver?",
        "answer": "2.5 Mbps maximum data transmission rate"
    },
    {
        "id": "tab25", "category": "table", "source_doc": "mcp2515_datasheet.pdf", "page": 2,
        "question": "What is the maximum CAN bus bit rate supported by the MCP2515 CAN controller?",
        "answer": "1.0 Mbps maximum CAN bit rate"
    },
    {
        "id": "tab26", "category": "table", "source_doc": "mcp2515_datasheet.pdf", "page": 2,
        "question": "What is the maximum SPI clock frequency for the MCP2515 interface?",
        "answer": "10.0 MHz maximum SPI clock frequency"
    },
    {
        "id": "tab27", "category": "table", "source_doc": "pca9685_datasheet.pdf", "page": 2,
        "question": "What is the default 7-bit I2C slave address for the PCA9685 controller when all address pins are grounded?",
        "answer": "0x40 (binary 1000000)"
    },
    {
        "id": "tab28", "category": "table", "source_doc": "pca9685_datasheet.pdf", "page": 2,
        "question": "How many independent PWM channels does the PCA9685 provide?",
        "answer": "16 independent PWM channels"
    },
    {
        "id": "tab29", "category": "table", "source_doc": "ch340g_datasheet.pdf", "page": 2,
        "question": "What is the maximum baud rate supported by the CH340G USB-to-UART bridge?",
        "answer": "2.0 Mbps (2000000 bps) maximum baud rate"
    },
    {
        "id": "tab30", "category": "table", "source_doc": "bme280_datasheet.pdf", "page": 2,
        "question": "What is the operating supply voltage range for the BME280 sensor?",
        "answer": "1.71V to 3.6V for VDD supply voltage"
    },
    {
        "id": "tab31", "category": "table", "source_doc": "bme280_datasheet.pdf", "page": 2,
        "question": "What is the humidity measurement accuracy tolerance of the BME280 sensor?",
        "answer": "±3% relative humidity tolerance"
    },
    {
        "id": "tab32", "category": "table", "source_doc": "dht22_datasheet.pdf", "page": 2,
        "question": "What is the temperature measurement range and accuracy of the DHT22 sensor?",
        "answer": "-40°C to +80°C with ±0.5°C accuracy"
    },
    {
        "id": "tab33", "category": "table", "source_doc": "mpu6050_datasheet.pdf", "page": 2,
        "question": "What is the maximum selectable gyroscope full-scale range on the MPU-6050?",
        "answer": "±2000 degrees per second (°/s)"
    },
    {
        "id": "tab34", "category": "table", "source_doc": "vl53l0x_datasheet.pdf", "page": 2,
        "question": "What is the maximum indoor ranging distance of the VL53L0X ToF sensor?",
        "answer": "2000 mm (2.0 meters) indoor ranging distance"
    },
    {
        "id": "tab35", "category": "table", "source_doc": "ina219_datasheet.pdf", "page": 2,
        "question": "What is the maximum bus voltage that can be monitored by the INA219 sensor?",
        "answer": "26V maximum bus voltage"
    },

    # ---------------- 3. DIAGRAM QUESTIONS (20) ----------------
    {
        "id": "img1", "category": "diagram", "source_doc": "dht22_datasheet.pdf", "page": 3,
        "question": "Which pin on the DHT22 4-pin package is the digital data I/O pin?",
        "answer": "Pin 2 (DATA)"
    },
    {
        "id": "img2", "category": "diagram", "source_doc": "lm7805_datasheet.pdf", "page": 3,
        "question": "In the standard LM7805 TO-220 pinout diagram, which pin is the Output pin?",
        "answer": "Pin 3 (Pin 1 is Input, Pin 2 is Ground/GND, Pin 3 is Output)"
    },
    {
        "id": "img3", "category": "diagram", "source_doc": "lm358_datasheet.pdf", "page": 3,
        "question": "In the LM358 8-pin DIP package pinout, which pins correspond to the inverting and non-inverting inputs of Amplifier 1?",
        "answer": "Pin 2 (1IN-) is inverting input and Pin 3 (1IN+) is non-inverting input"
    },
    {
        "id": "img4", "category": "diagram", "source_doc": "ne555_datasheet.pdf", "page": 3,
        "question": "In the NE555 8-pin DIP pinout, which pin is the Trigger input and which is the Output pin?",
        "answer": "Pin 2 is Trigger and Pin 3 is Output"
    },
    {
        "id": "img5", "category": "diagram", "source_doc": "max485_datasheet.pdf", "page": 3,
        "question": "In the MAX485 8-pin DIP pinout diagram, which pins are the differential transmission lines A and B?",
        "answer": "Pin 6 is Non-inverting driver output A, and Pin 7 is Inverting line B"
    },
    {
        "id": "img6", "category": "diagram", "source_doc": "l298n_datasheet.pdf", "page": 3,
        "question": "In the L298N Multiwatt-15 package pinout, which pins are Output 1 and Output 2 for Bridge A?",
        "answer": "Pin 2 (OUT1) and Pin 3 (OUT2)"
    },
    {
        "id": "img7", "category": "diagram", "source_doc": "esp32_datasheet.pdf", "page": 3,
        "question": "According to the ESP32 pinout diagram, which strapping pin is used to control download/boot mode?",
        "answer": "GPIO0 (Pin 25 / Strapping pin)"
    },
    {
        "id": "img8", "category": "diagram", "source_doc": "bme280_datasheet.pdf", "page": 3,
        "question": "In the BME280 LGA pinout diagram, which pin is the I2C Clock (SCL) and which is I2C Data (SDA)?",
        "answer": "Pin 4 is SCK/SCL and Pin 3 is SDI/SDA"
    },
    {
        "id": "img9", "category": "diagram", "source_doc": "lm7805_datasheet.pdf", "page": 3,
        "question": "In the LM7805 typical application circuit schematic, what recommended capacitor values are placed at the input and output terminals for stability?",
        "answer": "0.33 µF ceramic capacitor at input (Cin) and 0.1 µF capacitor at output (Cout)"
    },
    {
        "id": "img10", "category": "diagram", "source_doc": "ne555_datasheet.pdf", "page": 3,
        "question": "In the NE555 standard astable multivibrator schematic, which pin is connected to the timing resistor discharge path?",
        "answer": "Pin 7 (DISCH / Discharge)"
    },
    {
        "id": "img11", "category": "diagram", "source_doc": "rp2040_datasheet.pdf", "page": 3,
        "question": "According to the RP2040 pinout diagram, which default GPIOs are assigned to I2C0 SDA and SCL?",
        "answer": "GPIO0 is I2C0 SDA and GPIO1 is I2C0 SCL"
    },
    {
        "id": "img12", "category": "diagram", "source_doc": "stm32f103_datasheet.pdf", "page": 3,
        "question": "In the STM32F103 LQFP48 pinout diagram, which pins are USART1 Transmit (TX) and Receive (RX)?",
        "answer": "PA9 is USART1 TX and PA10 is USART1 RX"
    },
    {
        "id": "img13", "category": "diagram", "source_doc": "atmega328p_datasheet.pdf", "page": 3,
        "question": "In the ATmega328P 28-pin DIP pinout, which pins are the hardware I2C SDA and SCL pins?",
        "answer": "Pin 27 (PC4 / SDA) and Pin 28 (PC5 / SCL)"
    },
    {
        "id": "img14", "category": "diagram", "source_doc": "mpu6050_datasheet.pdf", "page": 3,
        "question": "In the MPU-6050 pinout diagram, which pin is the AD0 I2C address selection pin?",
        "answer": "Pin 9 is AD0 (Address Select)"
    },
    {
        "id": "img15", "category": "diagram", "source_doc": "vl53l0x_datasheet.pdf", "page": 3,
        "question": "In the VL53L0X pinout diagram, which pin is the XSHUT hardware shutdown pin?",
        "answer": "Pin 5 is XSHUT"
    },
    {
        "id": "img16", "category": "diagram", "source_doc": "ds18b20_datasheet.pdf", "page": 3,
        "question": "In the DS18B20 TO-92 3-pin package, which pin is the DQ 1-Wire data line?",
        "answer": "Pin 2 is DQ (1-Wire Data Line)"
    },
    {
        "id": "img17", "category": "diagram", "source_doc": "ina219_datasheet.pdf", "page": 3,
        "question": "In the INA219 pinout diagram, which pins connect across the current sensing shunt resistor?",
        "answer": "Pin 1 (IN+) and Pin 2 (IN-)"
    },
    {
        "id": "img18", "category": "diagram", "source_doc": "tb6612fng_datasheet.pdf", "page": 3,
        "question": "In the TB6612FNG pinout, which pin must be pulled HIGH to take the driver out of standby mode?",
        "answer": "Pin 21 (STBY / Standby Pin)"
    },
    {
        "id": "img19", "category": "diagram", "source_doc": "a4988_datasheet.pdf", "page": 3,
        "question": "In the A4988 stepper driver pinout, which pin receives the step pulse signal to advance the motor?",
        "answer": "STEP pin"
    },
    {
        "id": "img20", "category": "diagram", "source_doc": "ad620_datasheet.pdf", "page": 3,
        "question": "In the AD620 8-pin DIP pinout, which two pins are connected to the RG gain setting resistor?",
        "answer": "Pin 1 and Pin 8 (RG pins)"
    },

    # ---------------- 4. COMPARATIVE & COMPATIBILITY QUESTIONS (15) ----------------
    {
        "id": "comp1", "category": "table", "source_doc": "lm7805_datasheet.pdf", "page": 2,
        "question": "Compare the dropout voltage of the standard LM7805 regulator versus the AMS1117-3.3 LDO regulator.",
        "answer": "LM7805 has a 2.0V dropout voltage requiring 7V min input, whereas AMS1117 has a 1.1V low dropout voltage"
    },
    {
        "id": "comp2", "category": "table", "source_doc": "l298n_datasheet.pdf", "page": 2,
        "question": "What is the difference in output transistor technology and on-resistance between the L298N and TB6612FNG motor drivers?",
        "answer": "L298N uses bipolar transistors with high voltage drop, while TB6612FNG uses DMOS MOSFETs with low 0.5 Ohm RDS(on)"
    },
    {
        "id": "comp3", "category": "table", "source_doc": "pca9685_datasheet.pdf", "page": 2,
        "question": "Can the PCA9685 and INA219 share the same I2C bus if both have their address pins grounded?",
        "answer": "Both default to I2C address 0x40 when address pins are grounded, causing a bus address collision unless one address is modified"
    },
    {
        "id": "comp4", "category": "table", "source_doc": "bme280_datasheet.pdf", "page": 2,
        "question": "What are the default I2C addresses for the BME280 and MPU-6050 sensors?",
        "answer": "BME280 uses 0x76 (or 0x77) and MPU-6050 uses 0x68 (or 0x69), so they can safely coexist on the same I2C bus"
    },
    {
        "id": "comp5", "category": "text", "source_doc": "rp2040_datasheet.pdf", "page": 1,
        "question": "Is the Raspberry Pi RP2040 GPIO 5V tolerant when connecting a 5V sensor like the MAX485 or DHT22?",
        "answer": "No, RP2040 GPIOs are 3.3V only (IOVDD max 3.63V) and require a logic level shifter when interfacing with 5V signals"
    },
    {
        "id": "comp6", "category": "text", "source_doc": "stm32f103_datasheet.pdf", "page": 1,
        "question": "Are the STM32F103 I/O pins 5V tolerant compared to the RP2040?",
        "answer": "Yes, STM32F103 includes FT (Five-volt Tolerant) pins, unlike the RP2040 which is strictly 3.3V max"
    },
    {
        "id": "comp7", "category": "table", "source_doc": "mp1584_datasheet.pdf", "page": 2,
        "question": "Compare the current delivery capability of the MP1584 buck converter with the LM7805 linear regulator.",
        "answer": "MP1584 supplies up to 3.0A at high switching efficiency (92%), while LM7805 is limited to 1.5A and dissipates heat linearly"
    },
    {
        "id": "comp8", "category": "table", "source_doc": "ads1115_datasheet.pdf", "page": 2,
        "question": "What is the ADC resolution difference between the STM32F103 built-in ADC and the external ADS1115 converter?",
        "answer": "STM32F103 has a 12-bit ADC (4096 counts), whereas ADS1115 provides 16-bit high resolution (65536 counts)"
    },
    {
        "id": "comp9", "category": "table", "source_doc": "esp32_datasheet.pdf", "page": 2,
        "question": "Compare the SRAM capacity between the ESP32, RP2040, and STM32F103 microcontrollers.",
        "answer": "ESP32 has 520 kB SRAM, RP2040 has 264 kB SRAM, and STM32F103 has 20 kB SRAM"
    },
    {
        "id": "comp10", "category": "table", "source_doc": "mcp2515_datasheet.pdf", "page": 2,
        "question": "Compare the maximum communication speeds of MAX485 (RS485) and MCP2515 (CAN bus).",
        "answer": "MAX485 operates up to 2.5 Mbps, while MCP2515 CAN bus operates up to 1.0 Mbps"
    },
    {
        "id": "comp11", "category": "text", "source_doc": "uln2003a_datasheet.pdf", "page": 1,
        "question": "Why is the ULN2003A better suited for driving 5V unipolar stepper motors than high-side switches?",
        "answer": "It provides 7 low-side open-collector Darlington pairs with integrated common-cathode inductive clamp diodes"
    },
    {
        "id": "comp12", "category": "table", "source_doc": "drv8833_datasheet.pdf", "page": 2,
        "question": "Compare the minimum operating voltage of the DRV8833 versus the L298N motor driver.",
        "answer": "DRV8833 operates down to 2.7V for low-voltage battery robotics, whereas L298N logic requires at least 4.5V"
    },
    {
        "id": "comp13", "category": "diagram", "source_doc": "pca9685_datasheet.pdf", "page": 3,
        "question": "What pins are required to connect a PCA9685 PWM controller to an ESP32 microcontroller?",
        "answer": "Connect SDA to ESP32 I2C SDA (GPIO21 default), SCL to ESP32 I2C SCL (GPIO22 default), VDD to 3.3V, and GND to GND"
    },
    {
        "id": "comp14", "category": "diagram", "source_doc": "mcp2515_datasheet.pdf", "page": 3,
        "question": "What SPI bus lines are required to interface the MCP2515 CAN controller with an MCU?",
        "answer": "SCK (Clock), SI/MOSI (Data In), SO/MISO (Data Out), and /CS (Chip Select)"
    },
    {
        "id": "comp15", "category": "table", "source_doc": "a4988_datasheet.pdf", "page": 2,
        "question": "What are the logic high voltage requirements for the A4988 stepper driver control inputs (STEP, DIR)?",
        "answer": "Logic high is compatible with 3.0V to 5.5V logic supplies (VDD)"
    },
]


def generate_benchmark_file():
    os.makedirs(os.path.dirname(EVAL_SET_PATH), exist_ok=True)
    with open(EVAL_SET_PATH, "w") as f:
        json.dump(QUESTIONS, f, indent=2)
    print(f"Generated {len(QUESTIONS)} curated benchmark questions in {EVAL_SET_PATH}!")


if __name__ == "__main__":
    generate_benchmark_file()
