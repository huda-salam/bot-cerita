from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .page_composer import PageComposition

def render_page(composition: PageComposition, panel_images: dict[str, str], output_path: str, font_path: str | None = None) -> str:
    canvas = composition.canvas
    page = Image.new('RGB', (canvas.width, canvas.height), canvas.background)
    draw = ImageDraw.Draw(page)
    font = ImageFont.truetype(font_path, 36) if font_path else ImageFont.load_default()
    for placement in composition.panels:
        image_path = panel_images.get(placement.panel_id)
        if not image_path or not Path(image_path).exists():
            continue
        image = Image.open(image_path).convert('RGB')
        x = int(placement.x * canvas.width)
        y = int(placement.y * canvas.height)
        w = int(placement.width * canvas.width)
        h = int(placement.height * canvas.height)
        image.thumbnail((w, h), Image.Resampling.LANCZOS)
        px = x + (w - image.width) // 2
        py = y + (h - image.height) // 2
        page.paste(image, (px, py))
    for block in composition.text_blocks:
        text = str(block.get('text', ''))
        x = int(float(block.get('x', 0)) * canvas.width)
        y = int(float(block.get('y', 0)) * canvas.height)
        draw.text((x, y), text, fill=block.get('fill', '#000000'), font=font)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    page.save(output_path, quality=95)
    return output_path
