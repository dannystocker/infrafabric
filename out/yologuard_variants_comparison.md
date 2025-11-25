# IF.yologuard_v3 Variant Comparison

This comparison lists every external copy flagged by the filesystem indexes alongside the canonical `code/yologuard/src/IF.yologuard_v3.py` file.

| Variant | Path | Relationship to repo version | Notable differences |
| --- | --- | --- | --- |
| **mcp-multiagent-bridge** | `/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py` | Same line count (744) and equivalent code up to sample data; the only diffs occur inside the CLI test harness. | Uses an “sk-or-v1…” OpenAI API key and a longer JWT in the hardcoded examples; otherwise it matches the repo copy (same pattern list, dedupe logic, and Wu Lun summary). This variant is the best fit for a future merge since it already reflects the latest detection logic and filters.
| **digital-lab reproducibility bundle** | `/home/setup/digital-lab.ca/infrafabric/yologuard/REPRODUCIBILITY_COMPLETE/IF.yologuard_v3.py` | Older revision (676 lines) with a truncated header and reduced deduplication. | Missing the MIT/ownership header, returns the raw `results` list instead of the deduplicated matches (risking duplicates in `predecode_and_rescan`), and uses earlier sample tokens (`sk-or-v1…`, placeholder JWT). Otherwise the entropy, decoding, and relationship helpers remain intact.
| **Codex review bundle** | `/mnt/c/users/setup/Downloads/yologuard-codex-review/code/v3/IF.yologuard_v3.py` | Essentially the same code as the digital-lab copy (676 lines) with the same omissions. | Also lacks the license block, skips deduplication, and keeps the old placeholder tokens in the CLI harness. It does not include any extra patterns beyond the canonical list.

**Summary:** The mcp-multiagent-bridge copy is closest to the repo version and should be treated as the canonical donor for future merges. The digital-lab and Codex review copies are stable but lagging: both omit the deduplication safeguard, they lack licensing metadata, and their example tokens predate the current aggregator values.
