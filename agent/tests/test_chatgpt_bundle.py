import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from agent.scripts.build_chatgpt_bundle import FILES, build


class TestChatGPTBundle(unittest.TestCase):
    def test_bundle_is_reproducible_and_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            first = build(Path(directory) / "first.zip")
            second = build(Path(directory) / "second.zip")
            self.assertEqual(hashlib.sha256(first.read_bytes()).digest(),
                             hashlib.sha256(second.read_bytes()).digest())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(set(archive.namelist()), set(FILES))
                instructions = archive.read(
                    "chatgpt/en/PROJECT_INSTRUCTIONS.md"
                ).decode("utf-8")
        self.assertIn("Minecraft", instructions)
        self.assertIn("not a request to disable", instructions)


if __name__ == "__main__":
    unittest.main()
