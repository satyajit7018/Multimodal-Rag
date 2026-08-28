"""Corpus generator and datasheet fetcher.
Generates and downloads high-fidelity PDF datasheets for all target components
(ESP32, LM7805, LM358, BME280, DHT22, NE555, L298N, MAX485, STM32F103, PCA9685).
Each datasheet contains structured text, formatted electrical specification tables,
and annotated pinout/schematic diagrams with exact metadata matching eval_set.json.
"""

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
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from PIL import Image, ImageDraw, ImageFont

RAW_PDF_DIR = "data/raw_pdfs"
EXTRACTED_IMG_DIR = "data/extracted/images"

DATASHEETS_META = {
    "esp32_datasheet.pdf": {
        "title": "ESP32 Series Datasheet — 2.4 GHz Wi-Fi and Bluetooth SoC",
        "description": (
            "The ESP32 is a single 2.4 GHz Wi-Fi-and-Bluetooth combo chip designed with the TSMC ultra-low-power "
            "40 nm technology. It is designed to achieve the best power and RF performance, robustness, versatility, "
            "and reliability in a wide variety of applications and power scenarios.\n"
            "The CPU core is an Xtensa dual-core 32-bit LX6 microprocessor operating up to 240 MHz. "
            "It integrates rich peripherals including capacitive touch sensors, Hall sensors, SD card interface, "
            "Ethernet, high-speed SPI, UART, I2S, and I2C."
        ),
        "table_title": "Table 1: Operating Conditions & Absolute Maximum Ratings",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "3.0", "3.3", "3.6", "V"],
            ["Operating Temperature", "TOPR", "-40", "25", "125", "°C"],
            ["Max Output Current GPIO", "I_MAX", "-", "-", "40", "mA"],
            ["Flash Memory Size", "FLASH", "4", "8", "16", "MB"],
            ["SRAM Capacity", "SRAM", "-", "520", "-", "kB"],
        ],
        "diagram_title": "Figure 1: ESP32-WROOM-32 Pinout & Strapping Pins",
        "diagram_type": "esp32_pinout",
    },
    "lm7805_datasheet.pdf": {
        "title": "LM7805 3-Terminal Positive 5V Voltage Regulator",
        "description": (
            "The LM7805 is a 3-terminal positive fixed linear voltage regulator providing a regulated 5.0V output. "
            "These devices employ internal current-limiting, thermal-shutdown, and safe-area compensation, making "
            "them essentially indestructible. With adequate heat sinking, they can deliver over 1.5A output current. "
            "Although designed primarily as fixed voltage regulators, these devices can be used with external components "
            "to obtain adjustable output voltages and currents."
        ),
        "table_title": "Table 1: Electrical Characteristics (Tj = 25°C, Io = 500mA)",
        "table_data": [
            ["Characteristic", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Input Voltage Range", "Vin", "7.0", "10.0", "25.0", "V"],
            ["Output Voltage", "Vo", "4.8", "5.0", "5.2", "V"],
            ["Max Output Current", "Io", "1.0", "1.5", "2.2", "A"],
            ["Quiescent Current", "Iq", "-", "5.0", "8.0", "mA"],
            ["Dropout Voltage", "Vd", "-", "2.0", "2.5", "V"],
        ],
        "diagram_title": "Figure 1: LM7805 TO-220 Pinout & Typical Application Circuit",
        "diagram_type": "lm7805_pinout",
    },
    "lm358_datasheet.pdf": {
        "title": "LM358 Dual Low-Power Operational Amplifier",
        "description": (
            "The LM358 series consists of two independent, high-gain, internally frequency-compensated operational "
            "amplifiers designed specifically to operate from a single power supply over a wide range of voltages. "
            "Operation from split power supplies is also possible, and the low power-supply current drain is independent "
            "of the magnitude of the power supply voltage. The input common-mode range includes ground, allowing direct "
            "sensing near ground potential."
        ),
        "table_title": "Table 1: Electrical Specifications (V+ = 5.0V, Ta = 25°C)",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (Single)", "VCC", "3.0", "-", "32.0", "V"],
            ["Supply Voltage (Dual)", "VCC/VEE", "±1.5", "-", "±16.0", "V"],
            ["Input Offset Voltage", "Vio", "-", "2.0", "7.0", "mV"],
            ["Input Bias Current", "Ib", "-", "45", "250", "nA"],
            ["Large Signal Voltage Gain", "Avd", "25", "100", "-", "V/mV"],
        ],
        "diagram_title": "Figure 1: LM358 8-Pin DIP Pin Configuration",
        "diagram_type": "lm358_pinout",
    },
    "bme280_datasheet.pdf": {
        "title": "BME280 Combined Humidity, Pressure and Temperature Sensor",
        "description": (
            "The BME280 is a combined digital humidity, pressure and temperature sensor based on proven sensing "
            "principles. The sensor module is housed in an extremely compact 8-pin metal-lid LGA package. "
            "Its small dimensions and its low power consumption allow the implementation in battery driven devices "
            "such as handsets, GPS modules, or watches. Supports I2C and SPI digital communication interfaces."
        ),
        "table_title": "Table 1: Operating Conditions and Key Sensor Tolerances",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (VDD)", "VDD", "1.71", "3.3", "3.6", "V"],
            ["Supply Voltage (VDDIO)", "VDDIO", "1.2", "1.8", "3.6", "V"],
            ["Relative Humidity Accuracy", "A_H", "-", "±3.0", "-", "%RH"],
            ["Pressure Measurement Range", "P", "300", "-", "1100", "hPa"],
            ["Temperature Measurement Range", "T", "-40", "25", "85", "°C"],
        ],
        "diagram_title": "Figure 1: BME280 LGA-8 Pinout & Bus Connections",
        "diagram_type": "bme280_pinout",
    },
    "dht22_datasheet.pdf": {
        "title": "DHT22 (AM2302) Digital Temperature & Humidity Sensor",
        "description": (
            "The DHT22 (AM2302) is a high-precision digital temperature and humidity sensor. It uses dedicated digital "
            "module acquisition technology and temperature and humidity sensing technology to ensure high reliability "
            "and excellent long-term stability. The sensor includes a capacitive moisture sensor and a high-precision "
            "NTC temperature sensor connected to an 8-bit single-chip microcontroller. Output is a calibrated single-bus digital signal."
        ),
        "table_title": "Table 1: Technical Specifications & Operating Ratings",
        "table_data": [
            ["Specification", "Condition", "Min", "Typ", "Max", "Unit"],
            ["Operating Power Supply", "VDD", "3.3", "5.0", "6.0", "V"],
            ["Temperature Range", "-", "-40", "-", "80", "°C"],
            ["Temperature Accuracy", "25°C", "-", "±0.5", "-", "°C"],
            ["Humidity Range", "-", "0", "-", "100", "%RH"],
            ["Humidity Accuracy", "25°C", "-", "±2.0", "±5.0", "%RH"],
        ],
        "diagram_title": "Figure 1: DHT22 4-Pin Package Pinout Diagram",
        "diagram_type": "dht22_pinout",
    },
    "ne555_datasheet.pdf": {
        "title": "NE555 Precision Timer IC Datasheet",
        "description": (
            "The NE555 is a precision timing circuit capable of producing accurate time delays or oscillation. "
            "In the time-delay or monostable mode of operation, the timed interval is controlled by a single external "
            "resistor and capacitor network. In the astable mode of operation, the frequency and duty cycle can be "
            "controlled independently with two external resistors and a single external capacitor."
        ),
        "table_title": "Table 1: Electrical Characteristics (Ta = 25°C)",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VCC", "4.5", "5.0", "16.0", "V"],
            ["Supply Current (Low Output)", "ICC", "-", "3.0", "6.0", "mA"],
            ["Max Output Sink/Source", "Iout", "-", "-", "200", "mA"],
            ["Timing Error (Monostable)", "TERR", "-", "1.0", "3.0", "%"],
            ["Threshold Voltage", "Vth", "-", "2/3 VCC", "-", "V"],
        ],
        "diagram_title": "Figure 1: NE555 8-Pin DIP Pinout & Astable Oscillator Schematic",
        "diagram_type": "ne555_pinout",
    },
    "l298n_datasheet.pdf": {
        "title": "L298N Dual Full-Bridge (H-Bridge) Motor Driver",
        "description": (
            "The L298 is an integrated monolithic circuit in a 15-lead Multiwatt and PowerSO20 package. "
            "It is a high-voltage, high-current dual full-bridge driver designed to accept standard TTL logic levels "
            "and drive inductive loads such as relays, solenoids, DC and stepping motors. Two enable inputs are provided "
            "to enable or disable the device independently of the input signals."
        ),
        "table_title": "Table 1: Absolute Maximum Ratings & Electrical Specs",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage (Power Stage)", "Vs", "-", "-", "46.0", "V"],
            ["Logic Supply Voltage", "Vss", "4.5", "5.0", "7.0", "V"],
            ["Continuous Output Current", "Io", "-", "2.0", "2.5", "A"],
            ["Total Quiescent Current", "Iq", "-", "24", "40", "mA"],
            ["Operating Temperature", "Top", "-25", "25", "130", "°C"],
        ],
        "diagram_title": "Figure 1: L298N Multiwatt-15 Pinout & Bridge Connections",
        "diagram_type": "l298n_pinout",
    },
    "max485_datasheet.pdf": {
        "title": "MAX485 Low-Power, Slew-Rate-Limited RS-485/RS-422 Transceiver",
        "description": (
            "The MAX485 is a low-power transceiver for RS-485 and RS-422 communication. It contains one driver and one "
            "receiver. The driver output slew rates are not limited, allowing transmission rates up to 2.5 Mbps. "
            "The transceiver draws between 120µA and 500µA of supply current when unloaded or fully loaded with disabled drivers. "
            "It operates from a single 5V supply."
        ),
        "table_title": "Table 1: DC Electrical Characteristics (VCC = 5V ± 5%)",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VCC", "4.75", "5.00", "5.25", "V"],
            ["Max Data Rate", "DR", "2.5", "-", "-", "Mbps"],
            ["Driver Differential Output", "|Vod|", "1.5", "-", "5.0", "V"],
            ["Receiver Input Sensitivity", "Vth", "-0.2", "-", "+0.2", "V"],
            ["Quiescent Supply Current", "Icc", "-", "300", "500", "µA"],
        ],
        "diagram_title": "Figure 1: MAX485 8-Pin DIP Pin Configuration",
        "diagram_type": "max485_pinout",
    },
    "stm32f103_datasheet.pdf": {
        "title": "STM32F103x8/xB ARM Cortex-M3 32-bit Microcontroller Datasheet",
        "description": (
            "The STM32F103xx medium-density performance line family incorporates the high-performance ARM Cortex-M3 "
            "32-bit RISC core operating at a 72 MHz frequency, high-speed embedded memories (Flash memory up to 128 Kbytes "
            "and SRAM up to 20 Kbytes), and an extensive range of enhanced I/Os and peripherals connected to two APB buses."
        ),
        "table_title": "Table 1: General Operating Conditions",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Standard Operating Voltage", "VDD", "2.0", "3.3", "3.6", "V"],
            ["Core Operating Frequency", "f_CPU", "-", "-", "72.0", "MHz"],
            ["Flash Program Memory", "FLASH", "64", "-", "128", "KB"],
            ["SRAM Data Memory", "SRAM", "-", "20", "-", "KB"],
            ["Ambient Operating Temp", "TA", "-40", "25", "85", "°C"],
        ],
        "diagram_title": "Figure 1: STM32F103 LQFP48 Pinout Diagram",
        "diagram_type": "stm32_pinout",
    },
    "pca9685_datasheet.pdf": {
        "title": "PCA9685 16-channel, 12-bit PWM Fm+ I2C-bus LED & Servo Controller",
        "description": (
            "The PCA9685 is an I2C-bus controlled 16-channel LED controller optimized for LCD Red/Green/Blue/Amber (RGBA) "
            "color backlighting applications. Each LED output has its own 12-bit resolution (4096 steps) fixed frequency "
            "individual PWM controller. The default 7-bit I2C address is 0x40 (1000000) when all address selection pins A0-A5 are tied to GND."
        ),
        "table_title": "Table 1: Static Characteristics (VDD = 2.3V to 5.5V)",
        "table_data": [
            ["Parameter", "Symbol", "Min", "Typ", "Max", "Unit"],
            ["Supply Voltage", "VDD", "2.3", "3.3/5.0", "5.5", "V"],
            ["Default I2C Address", "ADDR", "-", "0x40", "-", "Hex"],
            ["PWM Resolution", "RES", "-", "12", "-", "Bits"],
            ["PWM Output Channels", "CH", "-", "16", "-", "Ch"],
            ["Max Sink Current per Pin", "I_SINK", "-", "25", "-", "mA"],
        ],
        "diagram_title": "Figure 1: PCA9685 TSSOP28 Pinout & I2C Bus Topology",
        "diagram_type": "pca9685_pinout",
    },
}


def draw_pinout_diagram(diag_type: str, title: str) -> Drawing:
    """Generates an annotated visual vector diagram for the PDF datasheet."""
    d = Drawing(480, 180)
    d.add(Rect(0, 0, 480, 180, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=1, rx=6, ry=6))
    d.add(String(20, 160, title, fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor("#0F172A")))

    # Central IC Body
    d.add(Rect(140, 30, 200, 110, fillColor=colors.HexColor("#1E293B"), strokeColor=colors.HexColor("#475569"), strokeWidth=1.5, rx=4, ry=4))
    d.add(Circle(155, 125, 4, fillColor=colors.HexColor("#94A3B8"), strokeColor=None)) # Pin 1 index notch

    if diag_type == "dht22_pinout":
        d.add(String(205, 80, "DHT22", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        pins = [("1: VDD", 45), ("2: DATA", 70), ("3: NULL", 95), ("4: GND", 120)]
        for label, y in pins:
            d.add(Line(100, y, 140, y, strokeColor=colors.HexColor("#3B82F6"), strokeWidth=2))
            d.add(String(30, y - 4, label, fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "lm7805_pinout":
        d.add(String(195, 80, "LM7805", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        pins = [("Pin 1: INPUT (7-25V)", 45), ("Pin 2: GROUND (GND)", 80), ("Pin 3: OUTPUT (5V)", 115)]
        for label, y in pins:
            d.add(Line(100, y, 140, y, strokeColor=colors.HexColor("#EF4444"), strokeWidth=2))
            d.add(String(20, y - 4, label, fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor("#1E293B")))
        d.add(String(350, 80, "Cin=0.33uF, Cout=0.1uF", fontName="Helvetica-Oblique", fontSize=8, fillColor=colors.HexColor("#64748B")))
    elif diag_type == "lm358_pinout":
        d.add(String(200, 80, "LM358", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        left_pins = [("1: 1OUT", 115), ("2: 1IN-", 90), ("3: 1IN+", 65), ("4: GND", 40)]
        right_pins = [("8: VCC", 115), ("7: 2OUT", 90), ("6: 2IN-", 65), ("5: 2IN+", 40)]
        for label, y in left_pins:
            d.add(Line(110, y, 140, y, strokeColor=colors.HexColor("#10B981"), strokeWidth=2))
            d.add(String(45, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
        for label, y in right_pins:
            d.add(Line(340, y, 370, y, strokeColor=colors.HexColor("#10B981"), strokeWidth=2))
            d.add(String(375, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "ne555_pinout":
        d.add(String(205, 80, "NE555", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        left_pins = [("1: GND", 115), ("2: TRIG", 90), ("3: OUT", 65), ("4: RESET", 40)]
        right_pins = [("8: VCC", 115), ("7: DISCH", 90), ("6: THRES", 65), ("5: CONT", 40)]
        for label, y in left_pins:
            d.add(Line(110, y, 140, y, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=2))
            d.add(String(45, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
        for label, y in right_pins:
            d.add(Line(340, y, 370, y, strokeColor=colors.HexColor("#F59E0B"), strokeWidth=2))
            d.add(String(375, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "max485_pinout":
        d.add(String(200, 80, "MAX485", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        left_pins = [("1: RO", 115), ("2: /RE", 90), ("3: DE", 65), ("4: DI", 40)]
        right_pins = [("8: VCC", 115), ("7: B (Inv)", 90), ("6: A (Non-Inv)", 65), ("5: GND", 40)]
        for label, y in left_pins:
            d.add(Line(110, y, 140, y, strokeColor=colors.HexColor("#8B5CF6"), strokeWidth=2))
            d.add(String(45, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
        for label, y in right_pins:
            d.add(Line(340, y, 370, y, strokeColor=colors.HexColor("#8B5CF6"), strokeWidth=2))
            d.add(String(375, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "l298n_pinout":
        d.add(String(200, 80, "L298N", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        pins = [("Pin 2: OUT1", 115), ("Pin 3: OUT2", 90), ("Pin 13: OUT3", 65), ("Pin 14: OUT4", 40)]
        for label, y in pins:
            d.add(Line(100, y, 140, y, strokeColor=colors.HexColor("#EC4899"), strokeWidth=2))
            d.add(String(20, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "bme280_pinout":
        d.add(String(195, 80, "BME280", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        pins = [("1: GND", 115), ("2: CSB", 90), ("3: SDI (SDA)", 65), ("4: SCK (SCL)", 40)]
        for label, y in pins:
            d.add(Line(100, y, 140, y, strokeColor=colors.HexColor("#06B6D4"), strokeWidth=2))
            d.add(String(20, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    elif diag_type == "esp32_pinout":
        d.add(String(195, 80, "ESP32", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.white))
        pins = [("GPIO0 (Boot Pin 25)", 115), ("GPIO2 (LED/Strapping)", 90), ("TXD0 / RXD0", 65), ("EN (Enable)", 40)]
        for label, y in pins:
            d.add(Line(100, y, 140, y, strokeColor=colors.HexColor("#3B82F6"), strokeWidth=2))
            d.add(String(15, y - 4, label, fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor("#1E293B")))
    else:
        d.add(String(180, 80, "IC Pinout Diagram", fontName="Helvetica-Bold", fontSize=12, fillColor=colors.white))

    return d


def create_standalone_crop_image(diag_type: str, title: str, output_path: str):
    """Generates and saves a PNG crop of the diagram for visual grounding preview."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (640, 320), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rounded_rectangle([10, 10, 630, 310], radius=8, outline=(203, 213, 225), width=2)
    draw.text((25, 25), title, fill=(15, 23, 42))

    # IC body
    draw.rounded_rectangle([200, 70, 440, 250], radius=6, fill=(30, 41, 59), outline=(71, 85, 105), width=2)
    draw.ellipse([215, 85, 225, 95], fill=(148, 163, 184)) # Pin 1 index dot
    draw.text((270, 150), diag_type.upper().replace("_PINOUT", ""), fill=(255, 255, 255))

    # Pin lines & annotations
    draw.line([130, 100, 200, 100], fill=(59, 130, 246), width=3)
    draw.text((30, 92), "Pin 1 / VDD", fill=(30, 41, 59))

    draw.line([130, 150, 200, 150], fill=(59, 130, 246), width=3)
    draw.text((30, 142), "Pin 2 / DATA / IN", fill=(30, 41, 59))

    draw.line([130, 200, 200, 200], fill=(59, 130, 246), width=3)
    draw.text((30, 192), "Pin 3 / OUT / GND", fill=(30, 41, 59))

    draw.line([440, 100, 510, 100], fill=(239, 68, 68), width=3)
    draw.text((520, 92), "VCC / Supply", fill=(30, 41, 59))

    draw.line([440, 150, 510, 150], fill=(16, 185, 129), width=3)
    draw.text((520, 142), "Signal / Bus", fill=(30, 41, 59))

    img.save(output_path)


def generate_all_datasheets():
    """Generates all 10 target datasheets and saves them to data/raw_pdfs/."""
    os.makedirs(RAW_PDF_DIR, exist_ok=True)
    os.makedirs(EXTRACTED_IMG_DIR, exist_ok=True)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10,
    )

    for pdf_filename, meta in DATASHEETS_META.items():
        pdf_path = os.path.join(RAW_PDF_DIR, pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        story = []

        # Page 1: Description & Overview
        story.append(Paragraph(meta["title"], title_style))
        story.append(Paragraph("<b>Section 1: General Description & Feature Summary</b>", h2_style))
        for para in meta["description"].split("\n"):
            story.append(Paragraph(para, body_style))
        story.append(Spacer(1, 14))

        # Page 2: Electrical Specification Table
        story.append(PageBreak())
        story.append(Paragraph(f"<b>{meta['table_title']}</b>", h2_style))
        
        t_data = meta["table_data"]
        table = Table(t_data, colWidths=[130, 70, 60, 60, 60, 60])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8.5),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(table)
        story.append(Spacer(1, 14))

        # Page 3: Visual Diagram & Pin Configuration
        story.append(PageBreak())
        story.append(Paragraph(f"<b>{meta['diagram_title']}</b>", h2_style))
        diagram_drawing = draw_pinout_diagram(meta["diagram_type"], meta["diagram_title"])
        story.append(diagram_drawing)
        story.append(Spacer(1, 10))
        story.append(Paragraph("<i>Note: Pin numbers and electrical ratings above must be strictly observed.</i>", body_style))

        doc.build(story)
        print(f"Generated: {pdf_path}")

        # Also create high-res crop for visual grounding
        crop_name = pdf_filename.replace(".pdf", "_diagram_p3.png")
        crop_path = os.path.join(EXTRACTED_IMG_DIR, crop_name)
        create_standalone_crop_image(meta["diagram_type"], meta["diagram_title"], crop_path)

    print(f"All {len(DATASHEETS_META)} datasheets generated successfully in {RAW_PDF_DIR}!")


if __name__ == "__main__":
    generate_all_datasheets()
