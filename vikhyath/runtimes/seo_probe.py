"""Runs INSIDE the SEO venv (`python -I seo_probe.py <run-dir>`): BeyondSEO's capture_quality for every captured
page of one run, as JSON lines. Stdlib + beyondseo only; never imports the vikhyath package."""
import json
import sys
from pathlib import Path

from beyondseo.evidence import capture_quality


def main(run_dir):
    for line in (Path(run_dir) / "pages.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            page = json.loads(line)
            print(json.dumps({"url": page.get("url"), "status": page.get("status"), "error": page.get("error"),
                              "quality": capture_quality(page)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
