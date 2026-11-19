import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from services import budget_service
from menus import menu_utils
from decimal import Decimal

console = Console()

budget_color = "#a395b8"

def budget_menu(connection):
    while True:
        console.clear()

        console.print(
            Panel(
                f"[bold {budget_color}]PERSONAL FINANCE TRACKER - BUDGET MENU[/bold {budget_color}]\n"
                "Manage your budgets",
                border_style=f"{budget_color}",
                padding=1
            )
        )

        choice = questionary.select(
            "Select an interaction:",
            choices=[
                "Set Budget",
                "Get Budgets",
                "Calculate Remaining Budget",
                "Back"
            ],
            qmark="",
            pointer="❯"
        ).ask()

        if choice is None or choice == "Back":
            return

        elif choice == "Set Budget":
            set_budget_prompt(connection)

        elif choice == "Get Budgets":
            get_budget_prompt(connection)

        elif choice == "Calculate Remaining Budget":
            calculate_remaining_budget_prompt(connection)

def set_budget_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {budget_color}]SET ACCOUNT BUDGETS[/bold {budget_color}]\n"
            "Create or update a budget for an account and category",
            border_style=f"{budget_color}",
            padding=1
        )
    )

    account_id = menu_utils.select_account(connection)

    if account_id is None:
        return

    category_id = menu_utils.select_category(connection)

    if category_id is None:
        return

    monthly_limit = questionary.text(
        "Budget Monthly Limit:",
        validate=lambda value: (
            "Please enter a limit."
            if not value
            else "Please enter a valid number."
            if not value.replace(".", "", 1).isdigit()
            else "Limit must be greater than 0."
            if float(value) <= 0
            else True
        )
    ).ask()

    if monthly_limit is None:
        return

    month = questionary.text(
        "Budget Month:",
        validate=lambda value: (
            "Please enter a month."
            if not value
            else "Month must be a number."
            if not value.isdigit()
            else "Month cannot be less than 1."
            if int(value) < 1
            else "Month cannot be greater than 12."
            if int(value) > 12
            else True
        )
    ).ask()

    if month is None:
        return

    year = questionary.text(
        "Budget Year:",
        validate=lambda value: (
            "Please enter a year."
            if not value
            else "Year must be a number."
            if not value.isdigit()
            else "Year cannot be less than 1."
            if int(value) < 1
            else True
        )
    ).ask()

    if year is None:
        return

    try:
        budget = budget_service.set_budget(
            connection, 
            account_id, 
            category_id, 
            Decimal(monthly_limit), 
            int(month), 
            int(year)
            )

        console.print(
            Panel(
                f"[bold green]Budget created/updated successfully![/bold green]\n\n"
                f"Budget ID: {budget["budget_id"]}\n"
                f"Account Name: {budget["account_name"]}\n"
                f"Category Name: {budget["category_name"]}\n"
                f"Budget Monthly Limit: ${budget["monthly_limit"]:,.2f}\n"
                f"Budget Month: {budget["budget_month"]}\n"
                f"Budget Year: {budget["budget_year"]}\n",
                border_style="green",
                padding=1
            )
        )

    except Exception as error:
        console.print(f"\n[bold red]Failed to create budget:[/bold red] {error}")

    questionary.text("\nPress Enter to return to the budgets menu.", qmark="").ask()

def get_budget_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {budget_color}]YOUR BUDGETS[/bold {budget_color}]\n"
            "View all budgets",
            border_style=f"{budget_color}",
            padding=1
        )
    )

    account_id = None
    month = None
    year = None

    choice = questionary.select(
        "Would you like to apply a filter:",
        choices=[
            "Filter by Account",
            "Filter by Month",
            "Filter by Year",
            "No filters"
        ],
        qmark="",
        pointer="❯"
    ).ask()

    if choice is None or choice == "No filters":
        pass

    elif choice == "Filter by Account":
        account_id = menu_utils.select_account(connection)

    elif choice == "Filter by Month":
        month = menu_utils.select_month(connection)

    elif choice == "Filter by Year":
        year = menu_utils.select_year(connection)

    budgets = budget_service.get_budgets(connection, account_id, month, year)

    if not budgets:
        console.print("\n[yellow]No budgets could be found...[/yellow]")

    else:
        table = Table(
            border_style=budget_color,
            header_style=f"bold {budget_color}",
            show_lines=True
        )

        table.add_column("Budget ID", justify="center")
        table.add_column("Account Name")
        table.add_column("Category Name")
        table.add_column("Budget Limit", justify="right")
        table.add_column("Budget Month")
        table.add_column("Budget Year")

        for budget in budgets:
            table.add_row(
                str(budget["budget_id"]),
                budget["account_name"],
                budget["category_name"],
                f"[green]${budget['monthly_limit']:,.2f}[/green]",
                str(budget["budget_month"]),
                str(budget["budget_year"]),
            )

        console.print(table)

    questionary.text("\nPress Enter to return to the budgets menu.", qmark="").ask()

def calculate_remaining_budget_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {budget_color}]REMAINING BUDGET LIMIT[/bold {budget_color}]\n"
            "View the remaining limit for a specific budget",
            border_style=f"{budget_color}",
            padding=1
        )
    )

    account_id = menu_utils.select_account(connection)

    if account_id is None:
        return

    budgets = budget_service.get_budgets(connection, account_id, None, None)

    if not budgets:
        console.print("\n[yellow]No budgets found for this account...[/yellow]")
        questionary.text(
            "\nPress Enter to return to the budgets menu.", 
            qmark=""
        ).ask()
        return

    choices = [
        questionary.Choice(
            title=(
                f"#{budget['budget_id']} | "
                f"{budget['budget_month']}/{budget['budget_year']} | "
                f"{budget['account_name']} | "
                f"{budget['category_name']} | "
                f"${budget['monthly_limit']:,.2f}"
            ),
            value=budget["budget_id"],
        )
        for budget in budgets
    ]

    selected_budget = questionary.select(
        "Select a budget:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

    if selected_budget is None:
        return

    try:
        remaining_budget = budget_service.get_budget_remaining(connection, selected_budget)

        if remaining_budget is None:
            console.print("[red]Budget not found.[/red]")
            return

        remaining = remaining_budget["remaining"]

        display_budget_color = "green" if remaining > 0 else "red"

        console.print()

        console.print(
            Panel(
                f"""
[bold]Monthly Limit:[/bold]  ${remaining_budget['monthly_limit']:,.2f}
[bold]Amount Spent:[/bold]   ${remaining_budget['amount_spent']:,.2f}
[bold]Remaining:[/bold]      [{display_budget_color}]${remaining:,.2f}[/{display_budget_color}]
                """,
                title=f"[bold {budget_color}]BUDGET OVERVIEW[/bold {budget_color}]",
                border_style=budget_color,
                expand=False
            )
        )

    except Exception as error:
        console.print(error)

    questionary.text("\nPress Enter to return to the budgets menu.", qmark="").ask()