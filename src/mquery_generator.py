_ALL_SLOTS = (
    [f"SUM_Measure_{i}" for i in range(1, 11)] +
    [f"CNT_Measure_{i}" for i in range(1, 6)] +
    [f"AVG_Measure_{i}" for i in range(1, 6)] +
    [f"Key_Dim_{i}" for i in range(1, 11)] +
    [f"Other_Field_{i}" for i in range(1, 11)] +
    ["DateKey"]
)


def generate_mquery(config):
    db = config["db"]
    if db == 4:
        return _csv_mquery(config)
    if db == 5:
        return _excel_mquery(config)
    raise NotImplementedError(f"M Query generation not yet supported for DB type {db}")


def _type_conversion_step(prev_step):
    pairs = []
    for i in range(1, 11):
        pairs.append(f'{{"SUM_Measure_{i}", Int64.Type}}')
    for i in range(1, 6):
        pairs.append(f'{{"CNT_Measure_{i}", Int64.Type}}')
    for i in range(1, 6):
        pairs.append(f'{{"AVG_Measure_{i}", type number}}')
    for i in range(1, 11):
        pairs.append(f'{{"Key_Dim_{i}", type text}}')
    for i in range(1, 11):
        pairs.append(f'{{"Other_Field_{i}", type text}}')
    pairs.append('{"DateKey", type date}')
    conversions = ", ".join(pairs)
    step = (
        f'    #"Changed Type" = Table.TransformColumnTypes({prev_step}, '
        f'{{{conversions}}})'
    )
    return '#"Changed Type"', step


def _remove_step(prev_step, unused_slots):
    if not unused_slots:
        return prev_step, None
    cols = ", ".join(f'"{s}"' for s in unused_slots)
    step = (
        f'    #"Removed Columns" = Table.RemoveColumns({prev_step}, {{{cols}}})'
    )
    return '#"Removed Columns"', step


def _rename_step(prev_step, field_map):
    if not field_map:
        return prev_step, None
    pairs = ",\n        ".join(
        f'{{"{src}", "{disp}"}}'
        for src, disp in field_map.items()
    )
    step = (
        f'    #"Renamed Columns" = Table.RenameColumns({prev_step}, {{\n'
        f'        {pairs}\n'
        f'    }})'
    )
    return '#"Renamed Columns"', step


def _csv_mquery(config):
    path = config["source"]
    field_map = config.get("field_map", {})
    unused_slots = config.get("unused_slots", [])

    source_expr = (
        f'    Source = Csv.Document(File.Contents("{path}"), '
        f'[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None])'
    )
    promote_expr = (
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])'
    )
    _, changed_type_expr = _type_conversion_step('#"Promoted Headers"')
    remove_final, remove_expr = _remove_step('#"Changed Type"', unused_slots)
    final_step, rename_expr = _rename_step(remove_final, field_map)

    steps = [source_expr, promote_expr, changed_type_expr]
    if remove_expr:
        steps.append(remove_expr)
    if rename_expr:
        steps.append(rename_expr)

    return "let\n" + ",\n".join(steps) + "\nin\n    " + final_step


def _excel_mquery(config):
    path = config["source"]
    field_map = config.get("field_map", {})
    unused_slots = config.get("unused_slots", [])

    source_expr = (
        f'    Source = Excel.Workbook(File.Contents("{path}"), null, true)'
    )
    sheet_expr = '    FirstSheet = Source{0}[Data]'
    promote_expr = (
        '    #"Promoted Headers" = Table.PromoteHeaders(FirstSheet, [PromoteAllScalars=true])'
    )
    _, changed_type_expr = _type_conversion_step('#"Promoted Headers"')
    remove_final, remove_expr = _remove_step('#"Changed Type"', unused_slots)
    final_step, rename_expr = _rename_step(remove_final, field_map)

    steps = [source_expr, sheet_expr, promote_expr, changed_type_expr]
    if remove_expr:
        steps.append(remove_expr)
    if rename_expr:
        steps.append(rename_expr)

    return "let\n" + ",\n".join(steps) + "\nin\n    " + final_step
