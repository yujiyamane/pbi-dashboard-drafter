# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PBI Dashboard Drafter — config-driven pipeline that generates Power BI PBIP/PBIR/TMDL files from a single SQL file containing a `/*FACTORY*/` comment block. Target: 90% of initial dashboard development automated; remaining 10% polished manually in PBI Desktop.

Full plan: [`docs/pbi-standard-template-plan.md`](docs/pbi-standard-template-plan.md)

Working directory: `C:\Users\Admin\Documents\Life\projects\pbi-dashboard-factory\`

## Commands

```powershell
# Run all tests
pytest

# Run a single test file
pytest tests/test_config_parser.py -v

# Run a single test by name
pytest tests/test_config_parser.py::test_parse_sum_fields -v
```

## Architecture

```
src/
  config_parser.py      # Parse /*FACTORY*/ block from SQL file → structured dict
  tmdl_generator.py     # Generate .tmdl files for Fact + Date tables (columns only, no DAX measures)
  mquery_generator.py   # Generate M Query for Oracle / PostgreSQL / Snowflake
  pbir_generator.py     # Generate .Report per-visual JSON files (PBIR format)
  rename_pipeline.py    # Global rename: TMDL display names + Report JSON simultaneously
  factory.py            # Orchestrator: config → parse → generate → rename → output
  validator.py          # Post-generation checks (duplicate keys, null patterns, Date types)
tests/
  fixtures/
    poc/                # POC PBIP fixtures for rename_pipeline integration tests
      poc.SemanticModel/
      poc.Report/
  test_config_parser.py
  test_tmdl_generator.py
  test_pbir_generator.py
  test_rename_pipeline.py
template/               # Golden master (read-only) — copy to output/ before rename
  Template.pbip
  Template.Report/
  Template.SemanticModel/
output/                 # Generated dashboards (not committed)
docs/
  pbi-standard-template-plan.md
```

## Key Rules

**Data model invariants:**

- `lineageTag` — generated as GUID at creation, **never modified**
- `sourceColumn` — maps to M Query output column name. Updated to match business name when M Query renames columns via Table.RenameColumns.
- Rename affects: (1) `name` property in TMDL, (2) field references in `.Report` visual JSON, (3) `sourceColumn` in TMDL when M Query uses Table.RenameColumns
- Unused slots are removed from M Query via `Table.RemoveColumns`. In TMDL they remain with `isHidden: true` + `IsAvailableInMDX: false` but carry no data.
- DATE fields must be `Date` type, not `DateTime`
- **DAX measures are not required for the initial draft** — Aggregation is handled at the visual level via `summarizeBy` (Aggregation field type in visual.json, `Function: 0` = Sum, `Function: 1` = Average, `Function: 3` = Distinct Count). Columns are renamed directly to business names. DAX can be used freely during manual polish; the key principle is to keep calculation logic consolidated — either in the SELECT statement (server-side) or in the source data preparation. Avoid scattering logic across DAX, M Query, and source SQL.
- **Always backup before rename** — Copy `template/` to `output/<project-name>/` before running `rename_pipeline`. Never skip this step.
- **Always delete cache.abf after TMDL edits** — Delete `<project>.SemanticModel/.pbi/cache.abf` after any TMDL modification or PBI Desktop shows stale state.
- **rename_pipeline scope** — Must only traverse `*.SemanticModel/` and `*.Report/` directories. Never traverse `template/` or `tests/fixtures/`. The `rename_pipeline` function uses `root.glob("*.SemanticModel")` and `root.glob("*.Report")` to enforce this.
- **definition.pbir must be patched** — `Template.Report/definition.pbir` contains a hardcoded `"path": "../template.SemanticModel"`. `run_factory` must update this to `"path": "../<ProjectName>.SemanticModel"` or PBI Desktop cannot find the semantic model.
- **.platform displayName must be patched** — Both `*.Report/.platform` and `*.SemanticModel/.platform` contain `"displayName": "template"`. `run_factory` must replace these with the project name, or PBI Desktop shows stale display names.
- **relationships.tmdl is a rename target** — `fromColumn: Fact.DateKey` and `toColumn:` entries in `relationships.tmdl` reference column names that get renamed (e.g. `DateKey` → `"Date Reported"`). `rename_tmdl` must handle `fromColumn`/`toColumn` patterns; omitting this causes a "relationship column not found" error in PBI Desktop.
- **Other_Field non-consecutive slots: use field_map** — When `6.OTHER:` specifies template slot names directly (e.g. `Other_Field_1 AS "Full Name", Other_Field_3 AS "Notes"`), `config["field_map"]` contains `{"Other_Field_1": ..., "Other_Field_3": ...}`. Both `_build_rename_map` (factory.py) and `get_hidden_columns` (visibility_pipeline.py) must detect `Other_Field_\d+` keys in `field_map` and use those slot numbers — NOT positional enumeration of `config["other"]`.
- **Hidden columns must be purged from visual.json projections** — `isHidden` in TMDL hides a column from the field list pane, but does NOT remove it from visuals that already have it bound. After `rename_pipeline`, call `remove_hidden_from_visuals(report_dir, hidden)` to delete unused-slot projection entries from every `visual.json`. Omitting this step leaves `Key_Dim_5`, `CNT_Measure_3`, etc. visible in table visuals. Both `Column.Property` and `Aggregation.Expression.Column.Property` must be checked; `Measure` projections are never removed.
- **page.json drillthrough filters — hidden fields must be removed from filterConfig** — Same principle as visual.json projections. After `remove_hidden_from_visuals`, call `remove_hidden_from_drillthrough_pages(report_dir, hidden)`. This removes filter entries from `filterConfig.filters` where `field.Column.Property` is hidden, and removes the matching `pageBinding.parameters` entries via the `boundFilter` UUID cross-reference. Omitting this step leaves unused-slot fields (e.g. `Other_Field_9`) as drillthrough parameters visible in the drillthrough panel.
- **DAX_ measures must be excluded from M Query field_map** — `_build_rename_map` adds `DAX_SUM_Measure_*` / `DAX_CNT_Measure_*` entries to `rename_map` for TMDL renaming. These are semantic model measures, NOT CSV columns. Before calling `generate_mquery()`, filter them out: `mquery_field_map = {k: v for k, v in rename_map.items() if not k.startswith("DAX_")}`. Passing the full `rename_map` causes PBI Desktop to throw "column not found" when evaluating the M Query.
- **Field Parameter tables (Select Dimension / Select 2nd Dimension / Select Measure) are rename targets** — These calculated partition tables contain `NAMEOF('Fact'[ColumnOrMeasure])` DAX expressions. `rename_field_parameters` in `rename_pipeline.py` must update both the row label and the NAMEOF reference, and must delete rows for unused slots. All three tables share the same structure and are processed by the same function via `semantic_root.rglob("*.tmdl")`.
- **en-US.tmdl must never be modified** — This file is auto-regenerated by PBI Desktop and contains localised display name overrides. Any manual edit will be silently discarded on next open. `rename_pipeline` already skips it via the `_DATE_TABLE_PREFIXES` guard; do not add it as a rename target.
- **rename_visual_json handles all visualTypes uniformly** — All chart types (tableEx, ribbonChart, barChart, lineChart, kpiCard, etc.) use the same JSON field reference patterns: `Property`, `queryRef`, `nativeQueryRef`, and `displayName` (ribbon chart Series). No visual-type-specific branching is needed; `rename_visual_json` applies string replacement across the entire file regardless of `visualType`.
- **page.json drillthrough filters: both rename AND hidden removal are required** — `rename_visual_json` handles `Property` renaming in `filterConfig` and `pageBinding.parameters.fieldExpr`. `remove_hidden_from_drillthrough_pages` removes entire filter+parameter pairs for hidden slots. Both must be applied: rename first (via `rename_pipeline`), then removal (via `remove_hidden_from_drillthrough_pages`). Applying only one leaves either stale template names or orphaned filter entries.
- **Visual field reference patterns are exhaustive** — `rename_visual_json` must cover all four patterns where field names appear in JSON: `"Property"`, `"queryRef": "Fact.<name>"`, `"queryRef": "Sum(Fact.<name>)"`, `"nativeQueryRef"` (suffix match), and `"displayName"`. Omitting any pattern causes silently-wrong output that PBI Desktop displays without error but with the wrong label.

**Slot limits:** SUM ×10, CNT ×5, AVG ×5, Key_Dim ×10, Other_Field ×10, ORDER columns (dynamic)

**DB connectivity patterns:**

| DB | M Query pattern | EnableFolding |
|---|---|---|
| Oracle | `Oracle.Database("server", [Query = "SELECT ..."])` | N/A |
| PostgreSQL | `Value.NativeQuery(PostgreSQL.Database(...), "SELECT ...", null, [EnableFolding=true])` | ✅ |
| Snowflake | `Value.NativeQuery(Snowflake.Databases(...), "SELECT ...", null, [EnableFolding=true])` | ✅ |

SELECT body is identical across all DB types — only the connection wrapper differs. Choose wrapper based on the `DB` setting in the config block.

**Naming:** Business English Title Case — `"Patient ID"`, `"Date Discharged"`, `"Length of Stay"`. Acronyms uppercase. Prepositions/articles lowercase.

**Sort columns:** `"ORDER [FieldName]"` in SELECT aliases the sort column. Post-rename pipeline strips the prefix, sets `sortByColumn` on the target field, and hides the ORDER column.

**Format specifiers:** `$` = currency, `#` = integer, `#.0` / `#.00` = 1/2 dp, `%` = percent. Default when omitted: `#,0.00`.

## Current Phase

**Phase 1 — Base Template Build** (in progress, building on POC success).

### Phase 0 — POC ✅ COMPLETE

Phase 0 proved all high-risk technical assumptions:
- `lineageTag`-safe rename: display names and `sourceColumn` updated to business names, GUIDs untouched
- Unused slot auto-hide: `isHidden: true` + `IsAvailableInMDX: false` injected correctly
- Full pipeline: `config_parser` → `mquery_generator` → `visibility_pipeline` → `format_pipeline` → `rename_pipeline` → `sort_pipeline` → `factory`
- Golden master template (40 columns) built in PBI Desktop and stored in `template/`
- Generated PBIP opens in PBI Desktop with zero errors

### Phase 1 — Base Template Build 🔄 LARGELY COMPLETE

- Field Parameter tables (Select Dimension / Select 2nd Dimension / Select Measure) built and pipeline-maintained
- DAX measures (DAX_SUM_Measure_* / DAX_CNT_Measure_*) renamed by pipeline; excluded from M Query field_map
- E2E validated: HR Dashboard + Finance Dashboard open in PBI Desktop with zero errors
- **321 automated tests — all passing**
