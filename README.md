# Superstore

Superstore is a marketplace for focused repository workflow plugins.

## Install from the marketplace

### Codex

```sh
codex plugin marketplace add coltonhyer/superstore
codex plugin add <plugin>@superstore
```

### Claude Code

```sh
claude plugin marketplace add coltonhyer/superstore --scope user
claude plugin install <plugin>@superstore --scope user
```

### Antigravity

Antigravity does not support third-party marketplace installation. Install plugins individually using the commands in their documentation.

## Plugins

| Name | Description | Documentation |
| --- | --- | --- |
| `library` | Archive finished Markdown into a verified SQLite ledger and restore it byte-for-byte. | [README](plugins/library/README.md) |

> [!NOTE]
> Make sure you've installed the marketplace before attempting to install any plugin via its documentation instructions

## Layout

```text
.agents/plugins/marketplace.json   # Codex marketplace
.claude-plugin/marketplace.json    # Claude Code marketplace
plugins/
  <plugin>/
    README.md
    .codex-plugin/plugin.json
    .claude-plugin/plugin.json
    plugin.json                    # Antigravity manifest
    ...
  ...
tests/test_marketplace.py
```

## Tests

```sh
python3 -m unittest discover -s tests
```
