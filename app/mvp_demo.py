from __future__ import annotations
from .page_composer import compose_page, PageCanvas
from .page_renderer import render_page

def build_demo_page(panel_images: dict[str, str], output_path: str) -> str:
    panel_ids = list(panel_images.keys())[:4]
    composition = compose_page(1, panel_ids, layout="two_by_two", canvas=PageCanvas())
    return render_page(composition, panel_images, output_path)

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Render a Bot Cerita one-page MVP demo")
    parser.add_argument("--output", default="artifacts/demo-page.jpg")
    parser.add_argument("panels", nargs="+", help="panel image paths")
    args = parser.parse_args()
    images = {f"panel-{i+1}": path for i, path in enumerate(args.panels)}
    print(build_demo_page(images, args.output))

if __name__ == "__main__":
    main()
