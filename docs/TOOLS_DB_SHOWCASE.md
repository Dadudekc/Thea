{{
# Tools Database Showcase

> Phase 3 milestone demonstration (CLI-only, zero GUI footprint)

This short guide illustrates how the new **Tools Database** works in practice.  
Everything runs from the terminal – no Dreamscape GUI required.

---

## 1. Quick Demo (30 sec)

```bash
# List tools now stored inside SQLite (auto-ingest on first run)
dreamos tools list

# Inspect any tool's source code with syntax highlighting
dreamos tools show hello_tool

# Execute a stored tool dynamically
dreamos tools run hello_tool -- "Victor"
```

### Expected output
```
Available CLI Tools
┌────┬─────────────────┐
│ #  │ Name            │
├────┼─────────────────┤
│ 1  │ hello_tool      │
│ 2  │ dreamos_cli     │
│ …  │ …               │
└────┴─────────────────┘
```

## 2. How It Works
1. `tools_db/ingest_tools.py` reads every file under `tools/` and stores the source in `data/tools.db`.
2. The **Dream.OS Toolbelt** (`dreamos tools …`) fetches code straight from that DB.
3. If you `import tools.<name>` after deleting the physical file, `tools/__init__.py` lazily materialises the module from the DB – seamless backwards-compatibility.

## 3. Recording Your Own Cast
We recommend recording an **asciinema** cast so reviewers can replay the session:
```bash
pip install asciinema  # one-time
asciinema rec docs/assets/tools_db_demo.cast -c "dreamos tools list && dreamos tools show hello_tool"
```
Then add the cast file to `docs/assets/` and reference it here:

```markdown
[![asciicast](https://asciinema.org/a/xxxxxxxx.png)](https://asciinema.org/a/xxxxxxxx)
```

*(Replace `xxxxxxxx` with the upload ID.)*

---

## 4. Next Steps
• Enable **remote tool packs** import via URL.  
• Add **versioning** (`v1`, `v2`, …) on `tools` table rows.  
• Provide **signature verification** for supply-chain security.

---

**Status:** ✅ *Showcase complete – Tools DB ready for production.*
}} 