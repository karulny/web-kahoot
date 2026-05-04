import io
import base64
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer


def generate_join_qr(pin: str, base_url: str = None) -> str:
    """
    Генерирует QR-код для подключения к игре.
    """
    pin = pin.upper().strip()
    
    if base_url:
        join_url = f"{base_url.rstrip('/')}/play/{pin}"
    else:
        join_url = f"/play/{pin}"
    
    # Создаём QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(join_url)
    qr.make(fit=True)
    
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color="#2c3e50",
        back_color="white"
    )
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"
