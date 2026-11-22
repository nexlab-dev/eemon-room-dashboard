"""Fail-closed tests for ZIP video integrity; no external media or network required.

Run: python3 -m unittest discover -s portal-v2/tests -p test_verify_release_zip.py -v
The strict integration with the real owner-held ZIP remains a separate release gate.
"""
import importlib.util
import pathlib
import tempfile
import unittest
import warnings
import zipfile

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "verify_release_zip.py"
spec = importlib.util.spec_from_file_location("eemon_verify_release_zip", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseZipIntegrityTests(unittest.TestCase):
    def archive(self, missing=None, duplicate=None, undersized=None, corrupt=False):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = pathlib.Path(folder.name) / "media.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
            for n in range(1, 11):
                name = f"{module.PREFIX}reel{n:02}.mp4"
                if n == missing:
                    continue
                data = b"x" * (module.MIN_BYTES if n == undersized else module.MIN_BYTES + 1)
                archive.writestr(name, data)
                if n == duplicate:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        archive.writestr(name, data)
        if corrupt:
            raw = bytearray(path.read_bytes())
            # Flip a stored payload byte without modifying the central directory CRC.
            pos = raw.find(b"x" * 20)
            self.assertGreater(pos, 0)
            raw[pos] ^= 1
            path.write_bytes(raw)
        return path

    def test_ten_unique_videos_accepted_as_media_only(self):
        videos = module.verify(self.archive())
        self.assertEqual(len(videos), 10)
        self.assertTrue(all(len(data) > module.MIN_BYTES for data in videos.values()))

    def test_missing_video_holds(self):
        with self.assertRaisesRegex(ValueError, "missing/undersized/duplicate"):
            module.verify(self.archive(missing=4))

    def test_undersized_video_holds(self):
        with self.assertRaisesRegex(ValueError, "missing/undersized/duplicate"):
            module.verify(self.archive(undersized=2))

    def test_duplicate_video_holds(self):
        with self.assertRaisesRegex(ValueError, "missing/undersized/duplicate"):
            module.verify(self.archive(duplicate=7))

    def test_crc_tampering_holds(self):
        with self.assertRaises(zipfile.BadZipFile):
            module.verify(self.archive(corrupt=True))

    def test_missing_archive_holds(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            module.verify(pathlib.Path("/unlikely/eemon-release-zip-not-found.zip"))


if __name__ == "__main__":
    unittest.main()
