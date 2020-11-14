from datasette import hookimpl
from datasette.utils import path_with_replaced_args
from datasette.utils.asgi import Response
import csv
import io
import tabulate


async def render_copyable(
    rows, columns, request, datasette, database, table, query_name
):
    table_format = request.args.get("_table_format")
    raw = request.args.get("_raw")

    # Look for {"value": "label":} dicts and turn them into just label
    new_rows = []
    for row in rows:
        new_row = []
        for cell in row:
            if isinstance(cell, dict):
                new_row.append(cell["label"])
            else:
                new_row.append(cell)
        new_rows.append(new_row)
    rows = new_rows

    if table_format not in tabulate.tabulate_formats:
        table_format = "tsv"

    if table_format == "tsv":
        writer = io.StringIO()
        csv_writer = csv.writer(writer, delimiter="\t")
        csv_writer.writerow(columns)
        for row in rows:
            csv_writer.writerow(row)
        copyable = writer.getvalue()
    else:
        copyable = tabulate.tabulate(rows, tablefmt=table_format, headers=columns)

    if raw:
        return {"body": copyable, "content_type": "text/plain; charset=utf-8"}

    return Response(
        await datasette.render_template(
            "copyable.html",
            {
                "database": database,
                "table": query_name or table,
                "table_format": table_format,
                "table_formats": [
                    {
                        "name": format_,
                        "link": path_with_replaced_args(
                            request, {"_table_format": format_}
                        ),
                    }
                    for format_ in tabulate.tabulate_formats
                ],
                "raw_link": path_with_replaced_args(request, {"_raw": "1"}),
                "copyable": copyable,
            },
            request=request,
        ),
        content_type="text/html; charset=utf-8",
    )


@hookimpl
def register_output_renderer(datasette):
    return {
        "extension": "copyable",
        "render": render_copyable,
    }
