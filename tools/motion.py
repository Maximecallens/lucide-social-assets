"""Motion design Lucide : rend une animation HTML image par image puis encode en MP4 (1080x1920, 30 fps).

Usage : python3 tools/motion.py <dossier>   (le dossier contient motion.html qui expose window.renderFrame(t) en secondes
                                           et window.DURATION ; produit video.mp4 + poster.jpg)
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS = 30


def render(folder):
    folder = Path(folder)
    html = (folder / "motion.html").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.set_content(html)
        pg.wait_for_timeout(500)
        duration = pg.evaluate("window.DURATION")
        n = int(duration * FPS)
        for i in range(n):
            pg.evaluate(f"window.renderFrame({i / FPS})")
            pg.screenshot(path=f"{tmp}/f{i:05d}.png")
        pg.evaluate(f"window.renderFrame({duration - 0.01})")
        pg.screenshot(path=str(folder / "poster.jpg"), type="jpeg", quality=90)
        b.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.png",
                        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100", "-shortest",
                        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "18",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(folder / "video.mp4")], check=True)
    print(folder / "video.mp4")


if __name__ == "__main__":
    render(sys.argv[1])
