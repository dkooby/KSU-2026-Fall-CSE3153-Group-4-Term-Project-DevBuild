from datetime import datetime
from decimal import Decimal

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from menus import menu_utils
from services import transaction_service, services_utils

console = Console()

transaction_color = "#e76f51"

def transaction_menu(connection):
    while True:
        console.clear()

        console.print(
            Panel(
                f"[bold {transaction_color}]PERSONAL FINANCE TRACKER - TRANSACTION MENU[/bold {transaction_color}]\n"
                "Manage your transactions",
                border_style=f"{transaction_color}",
                padding=1
            )
        )

        choice = questionary.select(
            "Select an interaction:",
            choices=[
                "Add Transaction",
                "Delete Transaction",
                "Update Transaction",
                "Back"
            ],
            qmark="",
            pointer="❯"
        ).ask()

        if choice is None or choice == "Back":
            return

        elif choice == "Add Transaction":
            add_transaction_prompt(connection)

        elif choice == "Delete Transaction":
            del_transaction_prompt(connection)

        elif choice == "Update Transaction":
            update_transaction_prompt(connection)

def add_transaction_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {transaction_color}]ADD NEW TRANSACTION[/bold {transaction_color}]\n"
            "Record a new income or expense",
            border_style=transaction_color,
            padding=1
        )
    )

    console.print(
        "\n[bold]Follow the prompts below to record your transaction.[/bold]"
    )

    account_id = menu_utils.select_account(connection)

    if account_id is None:
        return

    category_id = menu_utils.select_category(connection)

    if category_id is None:
        return

    merchant_id = None

    choice = questionary.select(
        "Would you like to associate a merchant with this transaction:",
        choices=[
            "Yes",
            "No"
        ],
        qmark="",
        pointer="❯"
    ).ask()

    if choice == "Yes":
        merchant_id = menu_utils.select_merchant(connection)

    transaction_amount = get_transaction_amount(connection)

    if transaction_amount is None:
        return

    transaction_date_input = get_transaction_date(connection)

    if transaction_date_input is None:
        return

    try:
        transaction_date = datetime.strptime(
            transaction_date_input,
            "%m/%d/%Y"
        )
    except ValueError:
        console.print("[red]Invalid date. Please use MM/DD/YYYY.[/red]")
        return

    transaction_description = get_transaction_description(connection)

    try:
        transaction = transaction_service.add_transaction(
            connection,
            account_id,
            category_id,
            transaction_amount,
            transaction_date,
            merchant_id,
            transaction_description
        )

        console.print(
            Panel(
                f"[bold green]Transaction saved successfully![/bold green]\n\n"
                f"Transaction ID: {transaction["transaction_id"]}\n"
                f"Account Name: {transaction["account_name"]}\n"
                f"Category Name: {transaction["category_name"]}\n"
                f"Merchant Name: {transaction.get('merchant_name') or 'N/A'}\n"
                f"Transaction Amount: ${transaction["transaction_amount"]:,.2f}\n"
                f"Transaction Date: {datetime.strftime(transaction["transaction_date"], "%B %d, %Y, %I:%M:%S %p")}\n"
                f"Transaction Description: {transaction.get('transaction_description') or 'N/A'}\n",
            border_style="green",
                padding=1
            )
        )

    except Exception as error:
        console.print(f"\n[bold red]Failed to save transaction:[/bold red] {error}")

    questionary.text("\nPress Enter to return to the transactions menu.", qmark="").ask()

def del_transaction_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {transaction_color}]DELETE TRANSACTION[/bold {transaction_color}]\n"
            "Delete a transaction from an account and update the account's balance",
            border_style=transaction_color,
            padding=1
        )
    )

    console.print("\n[bold]Follow the prompts below to delete a transaction.[/bold]")

    account_id = menu_utils.select_account(connection)

    if account_id is None:
        return

    transaction_id = menu_utils.select_transaction(connection, account_id)

    if transaction_id is None:
        return

    choice = questionary.select(
        "Are you sure you want to delete this transaction and update your account's balance (PERMANENT):",
        choices=[
            "NO, do not delete this transaction",
            "YES, delete this transaction",
        ],
        qmark="",
        pointer="❯"
    ).ask()

    if choice is None or choice == "NO, do not delete this transaction":
        return

    elif choice == "YES, delete this transaction":
        try:
            transaction_service.delete_transaction(connection, transaction_id)

            console.print(f"\n[green]Transaction deleted successfully.[/green]")

        except Exception as error:
            console.print(f"\n[bold red]Failed to delete transaction:[/bold red] {error}")

    questionary.text("\nPress Enter to return to the transactions menu.", qmark="").ask()

def update_transaction_prompt(connection):
    console.clear()

    console.print(
        Panel(
            f"[bold {transaction_color}]UPDATE TRANSACTION[/bold {transaction_color}]\n"
            "Update almost anything for a past transaction",
            border_style=transaction_color,
            padding=1
        )
    )

    console.print(
        "\n[bold]Follow the prompts below to update your transaction.[/bold]"
    )

    account_id = menu_utils.select_account(connection)

    if account_id is None:
        return

    transaction_id = menu_utils.select_transaction(connection, account_id)

    if transaction_id is None:
        return

    transaction = services_utils.get_transaction(connection, transaction_id)

    if transaction is None:
        console.print("[red]Transaction not found.[/red]")
        return

    category_id = None
    merchant_id = None
    transaction_amount = None
    transaction_date = None
    transaction_description = None

    updated_merchant = False
    updated_account = False

    while True:
        console.clear()

        console.print(
            Panel(
                f"[bold {transaction_color}]UPDATE TRANSACTION[/bold {transaction_color}]\n"
                "Update almost anything for a past transaction",
                border_style=transaction_color,
                padding=1
            )
        )

        display_transaction(
            connection,
            transaction,
            account_id,
            category_id,
            merchant_id,
            transaction_amount,
            transaction_date,
            transaction_description,
            updated_merchant,
            updated_account
        )

        choice = questionary.select(
            "Select the update(s) to make:",
            choices=[
                "Change Transaction Account",
                "Change Transaction Category",
                "Update Transaction Merchant",
                "Update Transaction Amount",
                "Update Transaction Date",
                "Update Transaction Description",
                "Submit Changes and Update Transaction",
                "Cancel Changes",
            ],
            qmark="",
            pointer="❯"
        ).ask()

        if choice == "Cancel Changes" or choice is None:
            return

        elif choice == "Change Transaction Account":
            account_id = menu_utils.select_account(connection)

            if account_id is None:
                return

            updated_account = True

        elif choice == "Change Transaction Category":
            category_id = menu_utils.select_category(connection)

            if category_id is None:
                return

        elif choice == "Update Transaction Merchant":
            merchant_id = menu_utils.select_merchant(connection)

            if merchant_id is None:
                return

            updated_merchant = True

        elif choice == "Update Transaction Amount":
            transaction_amount = get_transaction_amount(connection)

        elif choice == "Update Transaction Date":
            transaction_date_input = get_transaction_date(connection)

            try:
                transaction_date = datetime.strptime(
                    transaction_date_input,
                    "%m/%d/%Y"
                )
            except ValueError:
                console.print("[red]Invalid date. Please use MM/DD/YYYY.[/red]")
                return

        elif choice == "Update Transaction Description":
            transaction_description = get_transaction_description(connection)

        elif choice == "Submit Changes and Update Transaction":
            try:
                transaction = transaction_service.update_transaction(
                    connection,
                    transaction_id,
                    account_id,
                    category_id,
                    transaction_amount,
                    transaction_date,
                    merchant_id,
                    transaction_description
                )

                console.print(
                    Panel(
                        f"[bold green]Transaction updated successfully![/bold green]\n\n"
                        f"Transaction ID: {transaction["transaction_id"]}\n"
                        f"Account Name: {transaction["account_name"]}\n"
                        f"Category Name: {transaction["category_name"]}\n"
                        f"Merchant Name: {transaction.get('merchant_name') or 'N/A'}\n"
                        f"Transaction Amount: ${transaction["transaction_amount"]:,.2f}\n"
                        f"Transaction Date: {datetime.strftime(transaction["transaction_date"], "%B %d, %Y, %I:%M:%S %p")}\n"
                        f"Transaction Description: {transaction.get('transaction_description') or 'N/A'}\n",
                    border_style="green",
                        padding=1
                    )
                )

                questionary.text("\nPress Enter to return to the transactions menu.", qmark="").ask()
                return

            except Exception as error:
                console.print(f"\n[bold red]Failed to save transaction:[/bold red] {error}")

# Util functions to reduce redundancy
def get_transaction_amount(connection):
    return questionary.text(
        "Transaction amount:",
        validate=lambda value: (
            True if value.strip() else "Amount cannot be empty."
        )
    ).ask()

def get_transaction_date(connection):
    return questionary.text(
        "Enter transaction date (MM/DD/YYYY):",
        qmark=""
    ).ask()

def get_transaction_description(connection):
    return questionary.text(
        "Transaction description (optional):",
        validate=lambda value: (
            "Category name cannot be over 255 characters."
            if not (len(value.strip()) < 255)
            else True
        )
    ).ask()

# Transaction Display Helper
def display_transaction(connection, transaction, account_id, category_id, merchant_id, transaction_amount, transaction_date, transaction_description, updated_merchant, updated_account):
    is_income = transaction["category_type"] == "Income"

    if category_id is not None:
        category = services_utils.get_category_name(connection, category_id)

        is_income = category["category_type"] == "Income"

    display_account = (
        transaction["account_name"]
        if updated_account is False
        else f"[yellow]{services_utils.get_account_name(connection, account_id)}[/yellow]"
    )

    display_category = (
        transaction["category_name"]
        if category_id is None
        else f"[yellow]{category["category_name"]}[/yellow]"
    )

    display_merchant = (
        transaction["merchant_name"] or "N/A"
        if updated_merchant is False
        else f"[yellow]{services_utils.get_merchant_name(connection, merchant_id)}[/yellow]"
    )

    display_amount = (
        transaction["transaction_amount"]
        if transaction_amount is None
        else transaction_amount
    )

    display_date = (
        transaction["transaction_date"].strftime("%m/%d/%Y")
        if transaction_date is None
        else f"[yellow]{transaction_date.strftime("%m/%d/%Y")}[/yellow]"
    )

    display_description = (
        transaction["transaction_description"] or "N/A"
        if transaction_description is None
        else f"[yellow]{transaction_description}[/yellow]"
    )

    formatted_amount = (
        f"[green]+${Decimal(display_amount):.2f}[/green]"
        if is_income
        else f"[red]-${Decimal(display_amount):.2f}[/red]"
    )

    if transaction_amount is not None:
        formatted_amount = f"[yellow]{formatted_amount}[/yellow]"

    table = Table(title="Current Transaction", border_style=transaction_color, show_header=True)

    table.add_column("ID", justify="center")
    table.add_column("Account")
    table.add_column("Date")
    table.add_column("Category")
    table.add_column("Merchant")
    table.add_column("Description")
    table.add_column("Amount", justify="right")

    table.add_row(
        str(transaction["transaction_id"]),
        display_account,
        display_date,
        display_category,
        display_merchant,
        display_description,
        formatted_amount
    )

    console.print(table)