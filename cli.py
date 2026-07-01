"""
Beautiful CLI Entry Point for the Binance Futures Testnet Trading Bot.
Uses argparse and Rich terminal UI components for a premium user experience.
"""
import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

from bot.orders import execute_order
from bot.exceptions import TradingBotError, ValidationError, NetworkError, BinanceAPIError

# Create custom theme for beautiful terminal output
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "accent": "bold magenta"
})
console = Console(theme=custom_theme)

def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market BUY order
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  # Limit SELL order (requires price)
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 98500.00

  # Dry-run validation check
  python cli.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.5 --dry-run
        """
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT)"
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL", "buy", "sell"],
        help="Order side (BUY or SELL)"
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type (MARKET or LIMIT)"
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity (positive number)"
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Price required for LIMIT orders (positive number)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Runs local validation and simulation without making API requests"
    )
    
    return parser.parse_args()

def display_summary(title: str, symbol: str, side: str, order_type: str, quantity: float, price: Optional[float], dry_run: bool) -> None:
    """Renders the order request summary table."""
    table = Table(title=title, show_header=True, header_style="accent", box=None)
    table.add_column("Parameter", style="dim", width=15)
    table.add_column("Value", style="bold white")
    
    table.add_row("Symbol", symbol)
    table.add_row("Side", side)
    table.add_row("Order Type", order_type)
    table.add_row("Quantity", str(quantity))
    table.add_row("Price", f"${price:,.2f}" if price else "MARKET PRICE")
    table.add_row("Dry Run Mode", "[yellow]ENABLED[/yellow]" if dry_run else "[green]DISABLED[/green]")
    
    console.print(Panel(table, border_style="info", expand=False))

def main() -> None:
    """Main CLI execution flow."""
    console.print()
    console.print("[accent]=== Binance Futures Testnet Trading Bot ===[/accent]")
    console.print("[dim]A clean-architecture CLI backend client[/dim]\n")
    
    args = parse_arguments()
    
    # 1. Print request summary
    display_summary(
        title="[bold cyan]Order Request Summary[/bold cyan]",
        symbol=args.symbol.upper(),
        side=args.side.upper(),
        order_type=args.type.upper(),
        quantity=args.quantity,
        price=args.price,
        dry_run=args.dry_run
    )
    
    # 2. Place Order with live spinner
    status_msg = "Running validation & dry run simulation..." if args.dry_run else "Connecting & executing order on Binance Testnet..."
    
    try:
        with console.status(f"[info]{status_msg}[/info]", spinner="dots") as status:
            response = execute_order(
                symbol=args.symbol,
                side=args.side,
                order_type=args.type,
                quantity=args.quantity,
                price=args.price,
                dry_run=args.dry_run
            )
            
        # 3. Print Successful execution results
        console.print("\n[success]SUCCESS: ORDER PLACED[/success]")
        
        resp_table = Table(title="[bold green]Order Execution Response[/bold green]", show_header=True, header_style="success", box=None)
        resp_table.add_column("Field", style="dim", width=15)
        resp_table.add_column("Details", style="bold white")
        
        resp_table.add_row("Order ID", response.order_id)
        resp_table.add_row("Symbol", response.symbol)
        resp_table.add_row("Status", f"[success]{response.status}[/success]")
        resp_table.add_row("Side", response.side)
        resp_table.add_row("Executed Qty", str(response.executed_qty))
        resp_table.add_row("Avg Price", f"${response.avg_price:,.2f}" if response.avg_price > 0 else "N/A")
        
        if args.dry_run:
            console.print(Panel(resp_table, border_style="warning", title="[warning]Dry Run Simulation Results[/warning]"))
        else:
            console.print(Panel(resp_table, border_style="success", title="[success]Live Futures Testnet Results[/success]"))
            
    except ValidationError as ve:
        console.print(f"\n[error]VALIDATION ERROR:[/error] [white]{ve}[/white]")
        sys.exit(1)
    except NetworkError as ne:
        console.print(f"\n[error]NETWORK TIMEOUT / CONNECTION ERROR:[/error] [white]{ne}[/white]")
        sys.exit(1)
    except BinanceAPIError as bae:
        console.print(f"\n[error]BINANCE API ERROR (Code: {bae.code}):[/error] [white]{bae.message}[/white]")
        sys.exit(1)
    except TradingBotError as tbe:
        console.print(f"\n[error]TRADING BOT ERROR:[/error] [white]{tbe}[/white]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[error]UNEXPECTED SYSTEM FAILURE:[/error] [white]{e}[/white]")
        sys.exit(1)

if __name__ == "__main__":
    main()
