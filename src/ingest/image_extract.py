"""Diagram handling: preprocessing with OpenCV, OCR for any printed labels
or values, and a vision-model caption for the full figure.
"""

import base64

import cv2
import easyocr

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"])
    return _reader


def preprocess_diagram(image_path: str):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return img, contours


def ocr_diagram(image_path: str) -> str:
    results = get_reader().readtext(image_path, detail=0)
    return " ".join(results)


def caption_figure(image_path: str) -> str:
    """Send the cropped figure to a vision-capable model for a caption.
    Requires ANTHROPIC_API_KEY to be set in the environment.
    """
    import anthropic

    client = anthropic.Anthropic()
    with open(image_path, "rb") as f:
        image_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Describe this electronics diagram, including any labeled pins or values.",
                    },
                ],
            }
        ],
    )
    return response.content[0].text
