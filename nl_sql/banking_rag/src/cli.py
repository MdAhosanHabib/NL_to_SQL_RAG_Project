"""
Banking NL-to-SQL terminal interface.
Run: python main.py
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .graph import build_graph

console = Console()

INITIAL_STATE = {
    "question":        "",
    "schema_context":  "",
    "generated_sql":   "",
    "error_feedback":  None,
    "query_result":    None,
    "execution_error": None,
    "retry_count":     0,
    "final_answer":    "",
}


def print_results(rows: list[dict]) -> None:
    if not rows:
        console.print("[yellow]Query returned no rows.[/yellow]")
        return
    table = Table(show_header=True, header_style="bold cyan", box=None)
    for col in rows[0].keys():
        table.add_column(str(col), overflow="fold")
    for row in rows[:25]:
        table.add_row(*[str(v) if v is not None else "NULL" for v in row.values()])
    console.print(table)
    if len(rows) > 25:
        console.print(f"[dim]  … {len(rows) - 25} more rows not shown[/dim]")


def main():
    console.print(Panel.fit(
        "[bold cyan]Banking NL-to-SQL RAG[/bold cyan]\n"
        "[dim]LangGraph · Ollama · PostgreSQL[/dim]\n"
        "[dim]Type [bold]debug[/bold] to toggle SQL view · [bold]quit[/bold] to exit[/dim]",
        border_style="cyan",
    ))

    graph      = build_graph()
    debug_mode = False

    while True:
        try:
            question = console.input("\n[bold green]You ›[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye.[/yellow]")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            console.print("[yellow]Goodbye.[/yellow]")
            break
        if question.lower() == "debug":
            debug_mode = not debug_mode
            state = "ON" if debug_mode else "OFF"
            console.print(f"[yellow]Debug mode {state}[/yellow]")
            continue

        with console.status("[bold blue]Thinking…[/bold blue]", spinner="dots"):
            result = graph.invoke({**INITIAL_STATE, "question": question})

        if debug_mode and result.get("generated_sql"):
            console.print(Panel(
                result["generated_sql"],
                title="[yellow]Generated SQL[/yellow]",
                border_style="yellow",
            ))

        if result.get("query_result"):
            print_results(result["query_result"])

        console.print(Panel(
            result.get("final_answer", "—"),
            title="[green]Answer[/green]",
            border_style="green",
        ))

