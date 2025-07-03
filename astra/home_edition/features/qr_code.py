import qrcode
from typing import Optional

def generate_qr_code(data: str, file_path: str, box_size: int = 10, border: int = 4) -> Optional[str]:
    """
    Generates a QR code from the given data and saves it to a file.

    Args:
        data: The data to encode in the QR code (e.g., URL, text).
        file_path: The absolute path to save the QR code image (e.g., 'C:/Users/User/qrcode.png').
        box_size: The size of each box (pixel) in the QR code.
        border: The thickness of the border around the QR code.

    Returns:
        The file path of the generated QR code image if successful, None otherwise.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return file_path
    except Exception as e:
        # Log the exception here in a real application
        print(f"Error generating QR code: {e}")
        return None