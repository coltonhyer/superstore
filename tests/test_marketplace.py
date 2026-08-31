import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MarketplaceLayoutTests(unittest.TestCase):
    def test_library_is_a_self_contained_marketplace_plugin(self):
        codex = json.loads(
            (ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )

        self.assertEqual([plugin["name"] for plugin in codex["plugins"]], ["library"])
        self.assertEqual(
            codex["plugins"][0]["source"]["path"], "./plugins/library"
        )
        self.assertEqual([plugin["name"] for plugin in claude["plugins"]], ["library"])
        self.assertEqual(claude["plugins"][0]["source"], "./plugins/library")

        library = ROOT / "plugins/library"
        for relative in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "plugin.json",
            "skills/archiving-documentation/SKILL.md",
            "skills/read-archive/SKILL.md",
        ):
            self.assertTrue((library / relative).is_file(), relative)

        for relative in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "plugin.json",
            "skills",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
