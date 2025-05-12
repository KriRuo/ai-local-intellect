import sys
import os
import time
from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal
from backend.app.scrapers.rss_scraper import scrape_and_save_rss_feed
from backend.app.services.tagging_service import TaggingService
import json
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio

console = Console()

def load_rss_sources():
    rss_sources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rss_sources.json')
    if os.path.exists(rss_sources_path):
        with open(rss_sources_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def run_rss_scraping(db: Session):
    feeds = load_rss_sources()
    if not feeds:
        console.print("[red]No RSS sources found in rss_sources.json[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Running RSS scraping...", total=None)
        
        imported_count = 0
        skipped_count = 0
        failed_count = 0
        
        for feed in feeds:
            url = feed.get('url')
            source = feed.get('source')
            platform = feed.get('platform', 'RSS')
            
            if not url or not source:
                console.print(f"[yellow]Skipped feed due to missing url or source: {feed}[/yellow]")
                skipped_count += 1
                continue
                
            try:
                posts = scrape_and_save_rss_feed(db, url, source, platform)
                console.print(f"[green]✓[/green] Scraped {source}")
                imported_count += 1
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to scrape {source}: {str(e)}")
                failed_count += 1

    # Print summary
    table = Table(title="RSS Scraping Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    table.add_row("Imported", str(imported_count))
    table.add_row("Skipped", str(skipped_count))
    table.add_row("Failed", str(failed_count))
    table.add_row("Total", str(len(feeds)))
    console.print(table)

def run_tagging(db: Session, batch_size: int = 10):
    tagging_service = TaggingService()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Running tagging service...", total=None)
        
        try:
            stats = tagging_service.tag_new_posts(db, batch_size=batch_size)
            
            # Print summary
            table = Table(title="Tagging Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")
            table.add_row("Total Processed", str(stats['total_items']))
            table.add_row("Successful", str(stats['successful_items']))
            table.add_row("Failed", str(stats['failed_items']))
            table.add_row("Skipped", str(stats['skipped_items']))
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error running tagging service: {str(e)}[/red]")

def main_menu():
    while True:
        console.print("\n[bold cyan]AI Local Intellect Management[/bold cyan]")
        console.print("1. Run RSS Scraping")
        console.print("2. Run Tagging")
        console.print("3. Run Both (Scraping + Tagging)")
        console.print("4. Exit")
        
        choice = console.input("\n[bold yellow]Enter your choice (1-4): [/bold yellow]")
        
        db = SessionLocal()
        try:
            if choice == "1":
                run_rss_scraping(db)
            elif choice == "2":
                batch_size = int(console.input("[bold yellow]Enter batch size for tagging (default 10): [/bold yellow]") or "10")
                run_tagging(db, batch_size)
            elif choice == "3":
                run_rss_scraping(db)
                console.print("\n[bold cyan]Starting tagging process...[/bold cyan]")
                run_tagging(db)
            elif choice == "4":
                console.print("[bold green]Goodbye![/bold green]")
                break
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        finally:
            db.close()

if __name__ == "__main__":
    main_menu() 