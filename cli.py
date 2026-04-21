"""Command Line Interface for Trading Bot"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import logging

from bot import (
    BinanceFuturesClient,
    OrderManager,
    validate_order_params,
    setup_logging
)

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

class TradingBotCLI:
    """Main CLI application"""
    
    def __init__(self):
        """Initialize the trading bot CLI"""
        self.logger, self.log_file = setup_logging()
        self.client = None
        self.order_manager = None
        
    def check_credentials(self) -> bool:
        """Check if API credentials are available"""
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        if not api_key or not api_secret:
            console.print("[red]❌ Error:[/red] API credentials not found!")
            console.print("[yellow]Please create a .env file with:[/yellow]")
            console.print("BINANCE_API_KEY=your_api_key")
            console.print("BINANCE_API_SECRET=your_api_secret")
            return False
        
        return True
    
    def initialize_client(self):
        """Initialize the Binance client"""
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        self.client = BinanceFuturesClient(api_key, api_secret)
        self.order_manager = OrderManager(self.client)
        
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
╔══════════════════════════════════════════════╗
║     🚀 Binance Futures Trading Bot v1.0     ║
║         [Testnet Environment]               ║
╚══════════════════════════════════════════════╝
        """
        console.print(Panel(welcome_text, style="bold cyan"))
        console.print(f"[green]✓ Logging to:[/green] {self.log_file}\n")
    
    def display_order_summary(self, order_params: dict):
        """Display order summary table"""
        table = Table(title="📋 Order Summary", style="bold")
        table.add_column("Parameter", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Symbol", order_params.get('symbol', 'N/A'))
        table.add_row("Side", order_params.get('side', 'N/A'))
        table.add_row("Type", order_params.get('type', 'N/A'))
        table.add_row("Quantity", str(order_params.get('quantity', 'N/A')))
        
        if order_params.get('price'):
            table.add_row("Price", f"${order_params.get('price'):.2f}")
        
        console.print(table)
    
    def display_order_result(self, result: dict):
        """Display order result"""
        if result['success']:
            order = result['order']
            
            result_table = Table(title="✅ Order Successful", style="bold green")
            result_table.add_column("Field", style="cyan")
            result_table.add_column("Value", style="green")
            
            result_table.add_row("Order ID", str(order.get('orderId', 'N/A')))
            result_table.add_row("Status", order.get('status', 'N/A'))
            result_table.add_row("Symbol", order.get('symbol', 'N/A'))
            result_table.add_row("Side", order.get('side', 'N/A'))
            result_table.add_row("Type", order.get('type', 'N/A'))
            result_table.add_row("Quantity", order.get('origQty', 'N/A'))
            result_table.add_row("Executed", order.get('executedQty', '0'))
            
            if order.get('avgPrice') and float(order.get('avgPrice')) > 0:
                result_table.add_row("Avg Price", f"${float(order.get('avgPrice')):.2f}")
            
            console.print(result_table)
            console.print(f"\n[green]✓ {result['message']}[/green]")
            
        else:
            console.print(f"\n[red]❌ {result['message']}[/red]")
    
    def place_market_order(self, symbol: str, side: str, quantity: float):
        """Place a market order"""
        console.print(f"\n[bold yellow]Placing {side} MARKET order for {quantity} {symbol}...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing order...", total=None)
            result = self.order_manager.place_order(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=quantity
            )
        
        self.display_order_result(result)
        return result
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float):
        """Place a limit order"""
        console.print(f"\n[bold yellow]Placing {side} LIMIT order for {quantity} {symbol} @ ${price:.2f}...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Processing order...", total=None)
            result = self.order_manager.place_order(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                quantity=quantity,
                price=price
            )
        
        self.display_order_result(result)
        return result
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        console.print("\n[bold cyan]🎮 Interactive Trading Mode[/bold cyan]\n")
        
        while True:
            # Get order parameters
            console.print("\n[bold]Enter order details:[/bold]")
            
            symbol = Prompt.ask("Symbol", default="BTCUSDT")
            symbol = symbol.upper()
            
            side = Prompt.ask("Side", choices=["BUY", "SELL"], default="BUY")
            
            order_type = Prompt.ask("Order Type", choices=["MARKET", "LIMIT"], default="MARKET")
            
            quantity = Prompt.ask("Quantity")
            
            price = None
            if order_type == "LIMIT":
                price = float(Prompt.ask("Price (USDT)"))
            
            # Validate parameters
            validation = validate_order_params(symbol, side, order_type, quantity, price)
            
            if not validation['valid']:
                console.print("[red]Validation errors:[/red]")
                for error in validation['errors']:
                    console.print(f"  • {error}")
                continue
            
            validated = validation['validated']
            
            # Display summary
            self.display_order_summary(validated)
            
            # Confirm order
            if not Confirm.ask("\nConfirm order?", default=True):
                console.print("[yellow]Order cancelled[/yellow]")
                continue
            
            # Place order
            if order_type == "MARKET":
                self.place_market_order(
                    validated['symbol'],
                    validated['side'],
                    validated['quantity']
                )
            else:
                self.place_limit_order(
                    validated['symbol'],
                    validated['side'],
                    validated['quantity'],
                    validated['price']
                )
            
            # Ask for another order
            if not Confirm.ask("\nPlace another order?", default=False):
                break
    
    def single_order_mode(self, symbol: str, side: str, order_type: str, 
                         quantity: str, price: str = None):
        """Process a single order from command line arguments"""
        # Validate parameters
        validation = validate_order_params(symbol, side, order_type, quantity, price)
        
        if not validation['valid']:
            console.print("[red]Validation errors:[/red]")
            for error in validation['errors']:
                console.print(f"  • {error}")
            return False
        
        validated = validation['validated']
        
        # Display summary
        self.display_order_summary(validated)
        
        # Place order
        if order_type.upper() == "MARKET":
            result = self.place_market_order(
                validated['symbol'],
                validated['side'],
                validated['quantity']
            )
        else:
            result = self.place_limit_order(
                validated['symbol'],
                validated['side'],
                validated['quantity'],
                validated['price']
            )
        
        return result['success']
    
    def run(self, args=None):
        """Main entry point for CLI"""
        self.display_welcome()
        
        if not self.check_credentials():
            sys.exit(1)
        
        self.initialize_client()
        
        if args and args.get('interactive'):
            self.interactive_mode()
        elif args and all(k in args for k in ['symbol', 'side', 'type', 'quantity']):
            # Single order mode
            self.single_order_mode(
                args['symbol'],
                args['side'],
                args['type'],
                args['quantity'],
                args.get('price')
            )
        else:
            # Default to interactive mode
            self.interactive_mode()
        
        # Cleanup
        if self.client:
            self.client.close()
        
        console.print("\n[green]✓ Bot shutdown complete[/green]")

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--interactive', action='store_true', 
                       help='Run in interactive mode')
    parser.add_argument('--symbol', type=str, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('--side', choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--type', choices=['MARKET', 'LIMIT'], help='Order type')
    parser.add_argument('--quantity', type=str, help='Order quantity')
    parser.add_argument('--price', type=str, help='Price for limit orders')
    
    args = parser.parse_args()
    
    # Prepare arguments dict
    cli_args = {}
    if args.interactive:
        cli_args['interactive'] = True
    elif args.symbol and args.side and args.type and args.quantity:
        cli_args = {
            'symbol': args.symbol,
            'side': args.side,
            'type': args.type,
            'quantity': args.quantity,
            'price': args.price
        }
    
    # Run bot
    bot = TradingBotCLI()
    bot.run(cli_args if cli_args else {'interactive': True})

if __name__ == "__main__":
    main()