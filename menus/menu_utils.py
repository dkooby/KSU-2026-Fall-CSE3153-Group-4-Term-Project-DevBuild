import questionary
from rich.console import Console
from rich.panel import Panel

from services import account_service, services_utils

console = Console()

# Account Selection Helper
def select_account(connection):
    accounts = account_service.get_accounts(connection)

    if not accounts:
        console.print("\n[yellow]No accounts available.[/yellow]")
        questionary.text("Press Enter to continue.", qmark="").ask()
        return None

    choices = [
        questionary.Choice(
            title=f"{account['account_name']} ({account['account_type']})",
            value=account["account_id"],
        )
        for account in accounts
    ]

    return questionary.select(
        "Select an account:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

# Category Selection Helper
def select_category(connection):
    categories = services_utils.get_categories(connection)

    if not categories:
        console.print("\n[yellow]No categories available.[/yellow]")
        questionary.text("Press Enter to create one.", qmark="").ask()

        return create_category_prompt(connection)

    choices = [
        questionary.Choice(
            title=f"({category['category_type']}) - {category['category_name']}",
            value=category["category_id"],
        )
        for category in categories
    ]

    choices.append(questionary.Choice(
        title="Create a new category",
        value=-1
    ))

    choice = questionary.select(
        "Select a category or create a new one:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

    if choice == -1:
        return create_category_prompt(connection)
    else:
        return choice

# Create Category Prompt
def create_category_prompt(connection):
    console.print("\n[bold]Follow the prompts below to create a new category.[/bold]")

    category_name = questionary.text(
        "Category name:",
        validate=lambda value: (
            "Category name cannot be empty."
            if not (len(value.strip()) > 0)
            else "Category name cannot be over 50 characters."
            if not (len(value.strip()) < 50)
            else True
        )
    ).ask()

    if category_name is None:
        return

    category_type = questionary.select(
        "Category type:",
        choices=[
            "Income",
            "Expense",
        ],
        qmark="",
        pointer="❯"
    ).ask()

    if category_type is None:
        return

    try:
        category_id = services_utils.create_category(connection, category_name.strip(), category_type)

        console.print(
            Panel(
                f"[bold green]Category created successfully![/bold green]\n\n"
                f"Category ID: {category_id}\n"
                f"Category Name: {category_name.strip()}\n"
                f"Category Type: {category_type}\n",
                border_style="green",
                padding=1
            )
        )

        questionary.text("\nPress Enter to continue with this category.", qmark="").ask()
        return category_id

    except Exception as error:
        console.print(f"\n[bold red]Failed to create category:[/bold red] {error}")

# Merchant Selection Helper
def select_merchant(connection):
    merchants = services_utils.get_merchants(connection)

    if not merchants:
        console.print("\n[yellow]No merchants available.[/yellow]")
        questionary.text("Press Enter to create one.", qmark="").ask()

        return create_merchant_prompt(connection)

    choices = [
        questionary.Choice(
            title=f"{merchant['merchant_name']}",
            value=merchant["merchant_id"],
        )
        for merchant in merchants
    ]

    choices.append(questionary.Choice(
        title="Save a new merchant",
        value=-1
    ))

    choice = questionary.select(
        "Select a merchant or save a new one:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

    if choice == -1:
        return create_merchant_prompt(connection)
    else:
        return choice

# Create Category Prompt
def create_merchant_prompt(connection):
    console.print("\n[bold]Follow the prompts below to save a new merchant.[/bold]")

    merchant_name = questionary.text(
        "Merchant name:",
        validate=lambda value: (
            "Category name cannot be empty."
            if not (len(value.strip()) > 0)
            else "Category name cannot be over 100 characters."
            if not (len(value.strip()) < 100)
            else True
        )
    ).ask()

    if merchant_name is None:
        return

    try:
        merchant_id = services_utils.create_merchant(connection, merchant_name.strip())

        console.print(
            Panel(
                f"[bold green]Merchant saved successfully![/bold green]\n\n"
                f"Category ID: {merchant_id}\n"
                f"Category Name: {merchant_name.strip()}\n",
                border_style="green",
                padding=1
            )
        )

        questionary.text("\nPress Enter to continue with this merchant.", qmark="").ask()
        return merchant_id

    except Exception as error:
        console.print(f"\n[bold red]Failed to save merchant:[/bold red] {error}")

# Transaction Selection Helper
def select_transaction(connection, account_id):
    transactions = account_service.get_account_transactions(connection, account_id)

    if not transactions:
        console.print("\n[yellow]No transactions available.[/yellow]")
        questionary.text("Press Enter to continue.", qmark="").ask()
        return None

    choices = [
        questionary.Choice(
            title=(
                f"#{transaction['transaction_id']} | "
                f"{transaction['category_type']} | "
                f"{transaction['transaction_date'].strftime('%m/%d/%Y')} | "
                f"{transaction['category_name']} | "
                f"${transaction['transaction_amount']:,.2f} | "
                f"{transaction['merchant_name'] or 'N/A'}"
            ),
            value=transaction["transaction_id"],
        )
        for transaction in transactions
    ]

    return questionary.select(
        "Select a transaction:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

# Budget Month and Year Selection Helpers
def select_month(connection) -> int | None:
    months = services_utils.fetch_months(connection)

    if not months:
        console.print("\n[yellow]No months available.[/yellow]")
        questionary.text("Press Enter to continue.", qmark="").ask()
        return None

    choices = [
        questionary.Choice(
            title=f"Budget Month {month[0]}",
            value=month[0],
        )
        for month in months
    ]

    return questionary.select(
        "Select a month:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()

def select_year(connection) -> int | None:
    years = services_utils.fetch_years(connection)

    if not years:
        console.print("\n[yellow]No years available.[/yellow]")
        questionary.text("Press Enter to continue.", qmark="").ask()
        return None

    choices = [
        questionary.Choice(
            title=f"Budget Year {year[0]}",
            value=year[0],
        )
        for year in years
    ]

    return questionary.select(
        "Select a year:",
        choices=choices,
        qmark="",
        pointer="❯"
    ).ask()