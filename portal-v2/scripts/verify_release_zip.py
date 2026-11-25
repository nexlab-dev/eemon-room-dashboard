#!/usr/bin/env python3
"""Run strict EEMON release-media QA against the owner-held ZIP, without altering repo.

Usage: python3 portal-v2/scripts/verify_release_zip.py /path/to/EEMON_PORTAL_v2.zip
Requires Python standard library only. Does not publish or call any network.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "EEMON_PORTAL_v2/site/media/reels/"
MIN_BYTES = 100_000


def verify(archive):
    if not archive.is_file():
        raise ValueError("release ZIP not found")
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP integrity failed")
        files = {}
        for n in range(1, 11):
            name = f"{PREFIX}reel{n:02}.mp4"
            entries = [i for i in z.infolist() if i.filename == name]
            if len(entries) != 1 or entries[0].file_size <= MIN_BYTES:
                raise ValueError(f"missing/undersized/duplicate video: reel{n:02}.mp4")
            files[name] = z.read(entries[0])
        return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    try:
        videos = verify(args.zip_path)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"HOLD: {exc}", file=sys.stderr)
        return 1
    # Run actual source tests from an isolated copy. Never write MP4s into the
    # checkout, modify the production site, or assume ZIP alone authorizes release.
    with tempfile.TemporaryDirectory(prefix="eemon-release-qa-") as folder:
        import shutil
        isolated = Path(folder) / "portal-v2"
        shutil.copytree(ROOT, isolated, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        target = isolated / "site/media/reels"
        target.mkdir(parents=True, exist_ok=True)
        for name, data in videos.items():
            (target / Path(name).name).write_bytes(data)
        env = dict(os.environ, EEMON_RELEASE_MEDIA_REQUIRED="1")
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(isolated / "tests"),
             "-p", "test_*.py", "-v"],
            env=env, check=False
        )
        if result.returncode:
            print("HOLD: strict QA failed", file=sys.stderr)
            return result.returncode
    print("MEDIA_QA_PASS: 10 ZIP videos and strict source tests passed; NOT PUBLICATION APPROVAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
