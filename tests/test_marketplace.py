import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODEX_INDEX = ROOT / ".agents/plugins/marketplace.json"
CLAUDE_INDEX = ROOT / ".claude-plugin/marketplace.json"
MANIFESTS = (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "plugin.json",
)
IMPLEMENTATION_SKILLS = {
    "plans",
    "implementing-plans",
    "subagent-execution",
    "reviewing-implementation",
    "verifying-changes",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class MarketplaceLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codex_plugins = load_json(CODEX_INDEX)["plugins"]
        cls.claude_plugins = load_json(CLAUDE_INDEX)["plugins"]
        cls.codex = {
            plugin["name"]: plugin for plugin in cls.codex_plugins
        }
        cls.claude = {
            plugin["name"]: plugin for plugin in cls.claude_plugins
        }

    def test_marketplace_plugin_names_are_unique(self):
        for index, plugins in (
            ("Codex", self.codex_plugins),
            ("Claude", self.claude_plugins),
        ):
            with self.subTest(index=index):
                names = [plugin["name"] for plugin in plugins]
                self.assertEqual(len(names), len(set(names)))

    def test_marketplaces_agree(self):
        self.assertEqual(set(self.codex), set(self.claude))
        self.assertIn("planning", self.codex)
        self.assertIn("implementation", self.codex)

        for name in self.codex:
            with self.subTest(plugin=name):
                source = f"./plugins/{name}"
                self.assertEqual(self.codex[name]["source"]["path"], source)
                self.assertEqual(self.claude[name]["source"], source)

    def test_listed_plugins_are_self_contained(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for name in self.codex:
            plugin_root = ROOT / "plugins" / name
            with self.subTest(plugin=name):
                self.assertTrue((plugin_root / "README.md").is_file())
                self.assertTrue((plugin_root / "skills").is_dir())
                self.assertIn(f"(plugins/{name}/README.md)", root_readme)

                for relative in MANIFESTS:
                    manifest = plugin_root / relative
                    self.assertTrue(manifest.is_file(), str(manifest))
                    self.assertEqual(load_json(manifest)["name"], name)

    def test_plugin_json_files_parse(self):
        roots = (
            ROOT / ".agents/plugins",
            ROOT / ".claude-plugin",
            ROOT / "plugins",
        )
        for root in roots:
            for path in root.rglob("*.json"):
                with self.subTest(path=path.relative_to(ROOT)):
                    load_json(path)

    def test_implementation_has_the_five_public_skills(self):
        plugin_root = ROOT / "plugins/implementation"
        skills = {
            path.name
            for path in (plugin_root / "skills").iterdir()
            if path.is_dir()
        }
        readme = (plugin_root / "README.md").read_text(encoding="utf-8")

        self.assertEqual(skills, IMPLEMENTATION_SKILLS)
        self.assertEqual(
            load_json(plugin_root / ".codex-plugin/plugin.json")["skills"],
            "./skills/",
        )
        self.assertLessEqual(
            len(load_json(plugin_root / ".codex-plugin/plugin.json")["interface"]["defaultPrompt"]),
            3,
        )
        for skill in IMPLEMENTATION_SKILLS:
            with self.subTest(skill=skill):
                self.assertTrue((plugin_root / "skills" / skill / "SKILL.md").is_file())
                self.assertIn(f"(skills/{skill}/SKILL.md)", readme)

    def test_root_is_not_a_plugin(self):
        for relative in (*MANIFESTS, "skills"):
            self.assertFalse((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
