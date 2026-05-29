# Copilot Instructions

This repository is a deterministic Python pipeline that parses a FACTORY SQL block and produces Power BI PBIP/TMDL project output through parse_config -> run_factory.

## Project Context

- Python pipeline modules in src: config_parser.py, factory.py, mquery_generator.py, visibility_pipeline.py, format_pipeline.py, rename_pipeline.py, sort_pipeline.py
- Pure standard library implementation in the pipeline code
- Test suite uses pytest and currently has 350 tests that must remain green
- Template inputs and outputs are PBIP projects with Template.Report, Template.SemanticModel, PBIR, and TMDL artifacts

## Hard Rules

- Always use TDD: write a failing test before changing the factory contract
- Output target is Power BI PBIP project folders only
- Never commit real or health data; use synthetic CSV data only
- Use trunk-based development and run the full test suite before any PR

## Test Command

Run tests with:

python -m pytest -q
