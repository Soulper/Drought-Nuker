import requests
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print
from rich.text import Text
import time
from rich.style import Style
from rich.color import Color
from rich.theme import Theme


custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green"
})
console = Console(theme=custom_theme)


LIME_CYAN = ((0, 255, 0), (0, 255, 255))  
GOLD_ORANGE = ((255, 215, 0), (255, 140, 0)) 
RED_CRIMSON = ((255, 69, 0), (220, 20, 60)) 
CYAN_BLUE = ((0, 255, 255), (0, 191, 255))  

def make_gradient_prompt(prompt: str, default: str = "") -> str:
    prompt_text = prompt
    if default:
        prompt_text += f" ({default})"
    prompt_text += ": "
    
    console.print(gradient_text(prompt_text), end="")
    return input()

def gradient_text(text, start_color=(0, 255, 0), end_color=(0, 191, 255)):
    """Create text with a gradient from start_color to end_color"""
    result = Text()
    lines = text.split('\n')
    
    for line_idx, line in enumerate(lines):
        if not line.strip():
            if line_idx < len(lines) - 1:
                result.append('\n')
            continue
            
        chars = list(line)
        for i, char in enumerate(chars):
            ratio = i / (len(chars) - 1) if len(chars) > 1 else 0
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            
            result.append(char, style=Style(color=Color.from_rgb(r, g, b)))
            
        if line_idx < len(lines) - 1:
            result.append('\n')
    
    return result

def success_gradient(text):
    return gradient_text(text, *LIME_CYAN)  

def error_gradient(text):
    return gradient_text(text, *RED_CRIMSON)  

def info_gradient(text):
    return gradient_text(text, *CYAN_BLUE)  

def warning_gradient(text):
    return gradient_text(text, *GOLD_ORANGE)  

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = """
                                ╔═══════════════════════════════════════╗
                                ║                                       ║
                                ║        Webhook Nuker & Deleter        ║
                                ║                                       ║
                                ╚═══════════════════════════════════════╝
    """
    gradient_banner = gradient_text(banner, *LIME_CYAN)
    console.print(Panel(
        gradient_banner,
        border_style=Style(color=Color.from_rgb(*LIME_CYAN[1])),
        padding=(2, 2),
        title="[ Discord Webhook Nuker & Deleter ]",
        title_align="center",
        subtitle="[ Made by @soulisgone.s ]",
        subtitle_align="center"
    ))

def validate_webhook(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def send_message(webhook, message, progress, task):
    while True:
        try:
            response = requests.post(webhook, json={"content": message})
            
            if response.status_code == 204:
                progress.update(task, description="✓ " + info_gradient("Message sent successfully...").plain)
                return True
            elif response.status_code == 429:  
                retry_after = response.json().get('retry_after', 20)
                console.print(warning_gradient("⚠ Rate limited! Waiting 20 seconds..."))
                for i in range(20):
                    progress.update(task, description=warning_gradient(f"⚠ Rate limited! Waiting {20-i} seconds...").plain)
                    time.sleep(1)
                progress.update(task, description=info_gradient("↺ Retrying message...").plain)
                continue
            else:
                progress.update(task, description=error_gradient("✗ Failed to send message...").plain)
                return False
        except Exception as e:
            console.print(error_gradient(f"✗ Error: {str(e)}"))
            return False

def delete_webhook(webhook: str) -> bool:
    try:
        response = requests.delete(webhook)
        return response.status_code in [204, 200]
    except:
        return False

def create_gradient_progress() -> Progress:
    return Progress(
        SpinnerColumn(style=Style(color=Color.from_rgb(*LIME_CYAN[0])), spinner_name="dots12"),
        TextColumn(
            "[progress.description]{task.description}",
            style=Style(color=Color.from_rgb(*CYAN_BLUE[1]))
        ),
        BarColumn(
            complete_style=Style(color=Color.from_rgb(*LIME_CYAN[0])),
            finished_style=Style(color=Color.from_rgb(*LIME_CYAN[1])),
            bar_width=40
        ),
        TaskProgressColumn(
            style=Style(color=Color.from_rgb(*CYAN_BLUE[1]))
        ),
        expand=True
    )

def display_menu() -> str:
    separator = gradient_text("═" * 40)
    console.print()
    console.print(separator)
    console.print(gradient_text("Select Operation:"))
    console.print(success_gradient("1. ⚡ Spam Webhook"))
    console.print(error_gradient("2. ⛔ Delete Webhook"))
    console.print(separator)
    
    while True:
        choice = make_gradient_prompt("Enter choice (1-2)")
        if choice in ['1', '2']:
            return choice
        console.print(error_gradient("✗ Invalid choice. Please enter 1 or 2."))

def spam_webhook(webhook: str):
    
    message = make_gradient_prompt("Enter message to send")
    amount = int(make_gradient_prompt("Enter number of messages", default="1") or "1")
    
    console.print(info_gradient("⚡ Starting message delivery...\n"))
    
    
    with create_gradient_progress() as progress:
        task = progress.add_task("⟳ Initializing...", total=amount)
        
        success_count = 0
        fail_count = 0
        
        for i in range(amount):
            if send_message(webhook, message, progress, task):
                success_count += 1
            else:
                fail_count += 1
            
            progress.update(task, advance=1)
    
    
    separator = gradient_text("═" * 40)
    console.print()
    console.print(separator)
    console.print(gradient_text("Results Summary:"))
    if success_count > 0:
        console.print(success_gradient(f"✓ Successfully sent: {success_count}"))
    if fail_count > 0:
        console.print(error_gradient(f"✗ Failed attempts: {fail_count}"))
    console.print(separator)

def main():
    clear_screen()
    display_banner()
    
    while True:
        
        choice = display_menu()
        
       
        while True:
            webhook = make_gradient_prompt("Enter webhook URL")
            with console.status(info_gradient("⟳ Validating webhook...").plain, spinner_style=Style(color=Color.from_rgb(*CYAN_BLUE[1])), spinner="dots12"):
                if validate_webhook(webhook):
                    console.print(success_gradient("✓ Webhook validated successfully!"))
                    break
                else:
                    console.print(error_gradient("✗ Invalid webhook URL. Please try again."))
        
        
        if choice == '1':
            spam_webhook(webhook)
        else:
            console.print()
            console.print(warning_gradient("⚠ Attempting to delete webhook..."))
            with console.status(warning_gradient("⟳ Deleting...").plain, spinner_style=Style(color=Color.from_rgb(*GOLD_ORANGE[1])), spinner="dots12"):
                if delete_webhook(webhook):
                    console.print(success_gradient("✓ Webhook deleted successfully!"))
                else:
                    console.print(error_gradient("✗ Failed to delete webhook."))
        
        
        continue_op = make_gradient_prompt("\nContinue with another operation? (y/n)", default="y")
        if continue_op.lower() != 'y':
            break
    
    console.print()
    console.print(info_gradient("→ Press Enter to exit..."))
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(warning_gradient("\nOperation cancelled by user."))
    except Exception as e:
        console.print(error_gradient(f"\nAn error occurred: {str(e)}"))