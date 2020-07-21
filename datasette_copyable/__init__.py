from datasette import hookimpl
from datasette.utils import path_with_replaced_args
import tabulate


async def render_copyable(rows, request, datasette, database, table, query_name):
    table_format = request.args.get("_table_format")
    raw = request.args.get("_raw")

    if table_format not in tabulate.tabulate_formats:
        table_format = "tsv"

    copyable = tabulate.tabulate(rows, tablefmt=table_format)

    if raw:
        return {"body": copyable, "content_type": "text/plain; charset=utf-8"}

    return {
        "body": await datasette.render_template(
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
        "content_type": "text/html; charset=utf-8",
    }


@hookimpl
def register_output_renderer(datasette):
    return {
        "extension": "copyable",
        "render": render_copyable,
    }
