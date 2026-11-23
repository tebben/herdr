import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "config", Path(__file__).resolve().parents[1] / "scripts" / "config.py"
)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "config"
        self.home = self.root / "home"
        self.source.mkdir()
        self.home.mkdir()

    def write(self, base, path, value):
        target = base / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)
        return target

    def test_apply_backs_up_and_preserves_unmanaged_state(self):
        self.write(self.source, "keys.json", '{"global":{"alt-e":"mod.open:herdr-nvim"}}')
        self.write(self.home, "keys.json", '{"global":{}}')
        state = self.write(self.home, "shared.json", '{"private":"untouched"}')
        config.sync("apply", self.source, self.home, self.root)
        self.assertEqual((self.home / "keys.json").read_bytes(), (self.source / "keys.json").read_bytes())
        backups = list((self.root / ".backups").glob("*/keys.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(json.loads(backups[0].read_text()), {"global": {}})
        self.assertEqual(state.read_text(), '{"private":"untouched"}')

    def test_capture_only_refreshes_managed_files(self):
        self.write(self.source, "keys.json", "{}")
        self.write(self.home, "keys.json", '{"global":{"alt-e":"mod.open:herdr-nvim"}}')
        self.write(self.home, "shared.json", "{}")
        config.sync("capture", self.source, self.home, self.root)
        self.assertEqual((self.source / "keys.json").read_bytes(), (self.home / "keys.json").read_bytes())
        self.assertFalse((self.source / "shared.json").exists())

    def test_apply_backs_up_custom_mod_and_keeps_executable_mode(self):
        self.write(self.source, "mods/mine/main.js", "new source")
        original = self.write(self.home, "mods/mine/main.js", "old source")
        original.chmod(0o755)
        config.sync("apply", self.source, self.home, self.root)
        backups = list((self.root / ".backups").glob("*/mods/mine/main.js"))
        self.assertEqual(backups[0].read_text(), "old source")
        self.assertEqual(original.stat().st_mode & 0o777, 0o755)

    def test_invalid_json_prevents_all_writes(self):
        self.write(self.source, "keys.json", '{"global":{}}')
        self.write(self.source, "settings.json", "invalid")
        original = self.write(self.home, "keys.json", "{}")
        with self.assertRaises(ValueError):
            config.sync("apply", self.source, self.home, self.root)
        self.assertEqual(original.read_text(), "{}")
        self.assertFalse((self.root / ".backups").exists())

    def test_rejects_state_upstream_and_traversal(self):
        installed = {"layout:new-default": {}, "new-shipped-mod": {}}
        for path in (
            "shared.json", "../keys.json", "/keys.json", "layouts/main.json",
            "layouts/new-default.json", "mods/new-shipped-mod/main.js",
            "mods/herdr-nvim/main.js", "mods/mine/herdr.d.ts",
        ):
            with self.subTest(path=path), self.assertRaises(ValueError):
                config.owned(Path(path), installed)

    def test_rejects_symlink_before_writing(self):
        self.write(self.source, "keys.json", "{}")
        outside = self.write(self.root, "outside.json", '{"private":true}')
        (self.home / "keys.json").symlink_to(outside)
        with self.assertRaises(ValueError):
            config.sync("apply", self.source, self.home, self.root)
        self.assertEqual(outside.read_text(), '{"private":true}')


if __name__ == "__main__":
    unittest.main()
