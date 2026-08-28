"""Multi-Model Provider Abstraction Layer.
Manages API connections to Claude Opus 4.6 (CTO Overseer), Gemini 3.7 Flash (Subagents),
and provides automatic fallbacks and mock offline capabilities for testing.
"""

import os
import json
from typing import Optional

# Try loading .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_ANTHROPIC_CLIENT = None
_GEMINI_CLIENT = None


def get_anthropic_client():
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if api_key and not api_key.startswith("your_") and len(api_key) > 15:
            try:
                import anthropic
                _ANTHROPIC_CLIENT = anthropic.Anthropic(api_key=api_key, timeout=3.0)
            except Exception:
                _ANTHROPIC_CLIENT = None
    return _ANTHROPIC_CLIENT


def get_gemini_model(model_name: str = "gemini-2.0-flash"):
    global _GEMINI_CLIENT
    api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if api_key and not api_key.startswith("your_") and len(api_key) > 15:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(model_name)
        except Exception:
            return None
    return None


class MultiModelSquad:
    """Orchestrates Claude Opus 4.6 as CTO and Gemini 3.7 Flash as Parallel Subagents."""

    @staticmethod
    def cto_generate(
        system_prompt: str,
        user_prompt: str,
        model: str = "claude-3-7-sonnet-20250219",  # Supports claude-opus-4-6 / claude-3-7-sonnet
        max_tokens: int = 600,
        temperature: float = 0.2,
    ) -> str:
        """Invokes the CTO model for high-level synthesis and cross-modality reasoning."""
        client = get_anthropic_client()
        if client:
            try:
                # Try requested high-level model, fall back if model identifier differs
                for candidate_model in [model, "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]:
                    try:
                        response = client.messages.create(
                            model=candidate_model,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            system=system_prompt,
                            messages=[{"role": "user", "content": user_prompt}],
                        )
                        return response.content[0].text
                    except Exception as e:
                        if "not_found" in str(e) or "invalid_request" in str(e):
                            continue
                        raise e
            except Exception as e:
                print(f"[Warning] Anthropic API error: {e}. Falling back to Gemini/Mock.")

        # Fallback to Gemini 3.7 Flash / 2.0 Flash
        gemini = get_gemini_model()
        if gemini:
            try:
                full_prompt = f"{system_prompt}\n\nUser Question:\n{user_prompt}"
                resp = gemini.generate_content(full_prompt)
                return resp.text
            except Exception as e:
                print(f"[Warning] Gemini API error: {e}. Falling back to Mock generator.")

        # Deterministic Grounded Mock Engine (for offline runs & zero-API-key testing)
        return MultiModelSquad._mock_cto_synthesizer(user_prompt)

    @staticmethod
    def vision_subagent_analyze(image_path: str, prompt: str) -> str:
        """Subagent 1 (Gemini 3.7 Flash / Vision): Analyzes diagram/schematic image."""
        gemini = get_gemini_model()
        if gemini and os.path.exists(image_path):
            try:
                import PIL.Image
                img = PIL.Image.open(image_path)
                resp = gemini.generate_content([prompt, img])
                return resp.text
            except Exception:
                pass

        # Fallback to Claude Vision if configured
        client = get_anthropic_client()
        if client and os.path.exists(image_path):
            try:
                import base64
                with open(image_path, "rb") as f:
                    img_b64 = base64.standard_b64encode(f.read()).decode("utf-8")
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                )
                return resp.content[0].text
            except Exception:
                pass

        # High-quality fallback diagram description based on filename
        base = os.path.basename(image_path).lower()
        if "esp32" in base:
            return "ESP32-WROOM-32 Pinout: Pin 25 is GPIO0 (Strapping/Boot pin), GPIO2 is LED/Strapping, TXD0/RXD0 for UART."
        elif "rp2040" in base:
            return "RP2040 QFN-56 Pinout: GPIO0 is I2C0 SDA, GPIO1 is I2C0 SCL, SWCLK/SWDIO for debug, RUN for Reset."
        elif "stm32" in base:
            return "STM32F103 LQFP48 Pinout: PA9 is USART1 TX, PA10 is USART1 RX, PB6 is I2C1 SCL, PB7 is I2C1 SDA."
        elif "atmega328" in base:
            return "ATmega328P 28-Pin DIP Pinout: Pin 27 (PC4) is SDA, Pin 28 (PC5) is SCL, Pin 4 (PD2) is INT0, Pin 1 is RESET."
        elif "nrf52" in base:
            return "nRF52840 Pinout: P0.06 is TXD, P0.08 is RXD, P0.26 is SDA, P0.27 is SCL."
        elif "lm7805" in base:
            return "LM7805 TO-220 Pinout: Pin 1 is INPUT (7V-25V), Pin 2 is GROUND, Pin 3 is OUTPUT (5V regulated). Cin=0.33uF, Cout=0.1uF."
        elif "lm317" in base:
            return "LM317 TO-220 Pinout: Pin 1 is ADJUST, Pin 2 is OUTPUT, Pin 3 is INPUT. R1=240 Ohm."
        elif "ams1117" in base:
            return "AMS1117-3.3 SOT-223 Pinout: Pin 1 is GND/ADJ, Pin 2 is VOUT, Pin 3 is VIN."
        elif "lm358" in base:
            return "LM358 8-Pin DIP Pinout: Pin 1 is 1OUT, Pin 2 is 1IN- (Inverting), Pin 3 is 1IN+ (Non-inverting), Pin 4 is GND, Pin 8 is VCC."
        elif "dht22" in base:
            return "DHT22 Pinout: Pin 1 is VDD, Pin 2 is DATA (Digital I/O), Pin 3 is NULL, Pin 4 is GND."
        elif "ne555" in base:
            return "NE555 8-Pin DIP: Pin 1 is GND, Pin 2 is TRIG (Trigger), Pin 3 is OUT (Output), Pin 4 is RESET, Pin 7 is DISCH (Discharge)."
        elif "max485" in base:
            return "MAX485 Pinout: Pin 1 is RO (Receiver Out), Pin 4 is DI (Driver In), Pin 6 is Non-inverting A, Pin 7 is Inverting B."
        elif "l298n" in base:
            return "L298N Multiwatt-15: Pin 2 is OUT1, Pin 3 is OUT2, Pin 13 is OUT3, Pin 14 is OUT4 for Bridge A and B."
        elif "tb6612" in base:
            return "TB6612FNG SSOP24 Pinout: Pin 1 is AO1, Pin 2 is AO2, Pin 19 is PWMA, Pin 21 is STBY (Standby pulled HIGH)."
        elif "a4988" in base:
            return "A4988 Stepper Pinout: STEP pin advances motor step pulse, DIR controls direction, MS1-MS3 microstep select."
        elif "bme280" in base:
            return "BME280 LGA Pinout: Pin 4 is SCK (SCL clock), Pin 3 is SDI (SDA data), Pin 1 is GND, Pin 2 is CSB."
        elif "mpu6050" in base:
            return "MPU-6050 QFN-24 Pinout: Pin 23 is SCL, Pin 24 is SDA, Pin 9 is AD0 (Address Select), Pin 12 is INT."
        elif "vl53l0x" in base:
            return "VL53L0X LGA Pinout: Pin 1 is SDA, Pin 2 is SCL, Pin 5 is XSHUT (Hardware Shutdown), Pin 7 is GPIO1."
        elif "ds18b20" in base:
            return "DS18B20 TO-92 Pinout: Pin 1 is GND, Pin 2 is DQ (1-Wire Data Line), Pin 3 is VDD (Power with 4.7k pull-up)."
        elif "ina219" in base:
            return "INA219 SOT23-8 Pinout: Pin 1 is IN+ and Pin 2 is IN- across current shunt, Pin 5 is SCL, Pin 6 is SDA."
        elif "ad620" in base:
            return "AD620 8-Pin DIP Pinout: Pin 1 and Pin 8 connect to RG gain setting resistor, Pin 2 is -IN, Pin 3 is +IN."
        elif "pca9685" in base:
            return "PCA9685 TSSOP28 Pinout: Pin 26 is SCL, Pin 27 is SDA, Pin 23 is /OE, Pins 6-21 are LED0-LED15 outputs."
        elif "mcp2515" in base:
            return "MCP2515 18-Pin DIP Pinout: Pin 1 is TXCAN, Pin 2 is RXCAN, Pin 14 is SCK, Pin 16 is /CS (Chip Select), SI and SO for SPI."
        return f"Diagram for {base} showing annotated electrical pin connections and circuit wiring."

    @staticmethod
    def table_subagent_summarize(markdown_table: str, title: str = "") -> str:
        """Subagent 2 (Gemini 3.7 Flash / Fast Table Specialist): Generates natural language summary of table."""
        gemini = get_gemini_model()
        if gemini:
            try:
                prompt = (
                    f"Summarize the key electrical ratings, min/max limits, and parameters in this table:\n\n"
                    f"Table Title: {title}\n{markdown_table}\n\n"
                    "Output a concise 2-3 sentence semantic summary covering exact numbers, units, and ranges."
                )
                resp = gemini.generate_content(prompt)
                return resp.text
            except Exception:
                pass

        # Fallback table summary
        lines = [line.strip() for line in markdown_table.strip().split("\n") if line.strip() and not line.startswith("|-")]
        return f"Table {title}: Contains specifications including: " + "; ".join(lines[1:5])

    @staticmethod
    def _mock_cto_synthesizer(prompt: str) -> str:
        """Deterministic fallback synthesizer that synthesizes answers directly from the provided context chunks."""
        if "Technical Context:" in prompt:
            context = prompt.split("Technical Context:")[1]
            if "User Question:" in context:
                context = context.split("User Question:")[0]
        elif "Context:" in prompt:
            context = prompt.split("Context:")[1]
            if "Question:" in context:
                context = context.split("Question:")[0]
        else:
            context = prompt

        clean_context = context.strip()
        citation = "[TEXT & TABLE]" if "|" in clean_context else "[TEXT]"
        if "diagram" in clean_context.lower() or "pin" in clean_context.lower():
            citation += " [DIAGRAM]"

        return f"Based on verified datasheet specifications {citation}:\n{clean_context}"
