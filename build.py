from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

WASM_DEPENDENCIES = [
    (
        "https://pygame-web.github.io/cdn/cp312/pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl",
        Path("static/cdn/cp312/pygame_ce-2.5.7-cp312-cp312-wasm32_bi_emscripten.whl"),
    ),
    (
        "https://pygame-web.github.io/cdn/index-0.9.3-cp312.json",
        Path("static/cdn/index-0.9.3-cp312.json"),
    ),
]


def prepare_static_assets(root: Path):
    """Ensure required WebAssembly runtime wheels and indices exist in static/cdn."""
    for url, rel_path in WASM_DEPENDENCIES:
        target = root / rel_path
        if not target.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            print(f"Downloading {target.name}...")
            urllib.request.urlretrieve(url, target)


def run_build():
    root = Path(__file__).resolve().parent
    build_dir = root / "build" / "web"

    try:
        import pygbag  # noqa: F401
    except ImportError:
        print("ERROR: pygbag not found. Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    prepare_static_assets(root)

    logo = root / "logo.png"
    if logo.is_file():
        (root / "static").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(logo, root / "static" / "logo.png")

    cmd = [
        sys.executable, "-m", "pygbag", "--build",
        "--template", "default.tmpl",
        "--title", "Goblin Slayer",
        "--width", "960", "--height", "600",
        str(root)
    ]
    res = subprocess.run(cmd, cwd=str(root))
    if res.returncode != 0:
        sys.exit(res.returncode)

    if logo.is_file():
        shutil.copyfile(logo, build_dir / "logo.png")

    if not (build_dir / "index.html").is_file():
        print("Build failed: index.html not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Build complete -> {build_dir}")


if __name__ == "__main__":
    run_build()
