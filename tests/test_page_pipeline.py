from pathlib import Path
from PIL import Image
from app.page_composer import compose_page
from app.page_renderer import render_page

def make_panel(path: Path, size=(600, 600)) -> None:
    Image.new('RGB', size, 'white').save(path)

def test_one_page_pipeline(tmp_path: Path):
    paths = []
    for i in range(4):
        path = tmp_path / f'panel-{i}.jpg'
        make_panel(path)
        paths.append(path)
    images = {f'panel-{i}': str(path) for i, path in enumerate(paths)}
    composition = compose_page(1, list(images), 'two_by_two')
    output = tmp_path / 'page.jpg'
    result = render_page(composition, images, str(output))
    assert result == str(output)
    assert output.exists()
    rendered = Image.open(output)
    assert rendered.size == (1600, 2400)
