import asyncio
import aiohttp
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Function to generate a new temporary email
async def get_temp_email(session):
    async with session.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1") as response:
        emails = await response.json()
        return emails[0]

# Function to generate multiple temporary emails in quick succession
async def spam_emails(session, num_emails):
    generated_emails = []
    for _ in range(num_emails):
        email = await get_temp_email(session)
        generated_emails.append(email)
        console.print(f"[green]Generated email: {email}[/green]")
        await asyncio.sleep(0.1)  # Slight delay to avoid overwhelming the server

    return generated_emails

# Function to get the details of a specific email by its ID
async def get_email_details(session, email, message_id):
    username, domain = email.split('@')
    async with session.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={message_id}") as response:
        message_details = await response.json()
        return message_details

# Function to display email messages in a table format
def display_email_message(details):
    table = Table(title="New Email Received", box=box.SQUARE)
    table.add_column("Field", style="cyan", justify="right")
    table.add_column("Content", style="magenta")
    
    table.add_row("From", details['from'])
    table.add_row("Subject", details['subject'])
    table.add_row("Body", details['textBody'])
    
    console.print(table)

# Function to check for new messages in the inbox
async def check_email_inbox(session, email):
    username, domain = email.split('@')
    while True:
        try:
            async with session.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}") as response:
                messages = await response.json()
                if messages:
                    for message in messages:
                        message_details = await get_email_details(session, email, message['id'])
                        display_email_message(message_details)
                else:
                    console.print(f"[yellow]No new messages for {email}.[/yellow]")
        except aiohttp.ClientConnectionError:
            console.print(f"[red]Connection error for {email}. Retrying in 10 seconds...[/red]")
        
        await asyncio.sleep(10)  # Check every 10 seconds

# Function to sign up an email for a Spotify account
async def signup_spotify(session, email):
    url = "https://www.spotify.com/signup"  # This should be the URL to the Spotify signup endpoint

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    form_data = {
        'email': email,
        'password': 'RandomPassword123',  # Use a secure random password generator
        'displayname': email.split('@')[0],  # Just using the username part of the email as the display name
        'dob_day': '01',
        'dob_month': '01',
        'dob_year': '1990',
        'gender': 'neutral',
        'key': 'signup-key'
        # Include all other required fields that Spotify asks for during sign-up
    }

    try:
        async with session.post(url, data=form_data, headers=headers) as response:
            if response.status == 200:
                console.print(f"[green]Signed up {email} to Spotify successfully![/green]")
            else:
                console.print(f"[red]Failed to sign up {email}. Status code: {response.status}[/red]")
    except Exception as e:
        console.print(f"[red]Error while signing up {email}: {e}[/red]")

# Function to sign up all generated emails to Spotify
async def signup_all_emails(emails):
    async with aiohttp.ClientSession() as session:
        for email in emails:
            await signup_spotify(session, email)

# Function to display credits
def display_credits():
    console.print("\n[bold cyan]--- Credits ---[/bold cyan]")
    console.print("[green]This AIO script was developed by numb.[/green]")
    console.print("[green]Feel free to use and share it![/green]\n")

# Menu system for the AIO script
async def menu():
    emails = []

    # Display the "Developed by numb" message when the script starts
    console.print("\n[bold cyan]--- Welcome to the AIO Script ---[/bold cyan]")
    console.print("[green]Developed by numb[/green]\n")

    async with aiohttp.ClientSession() as session:
        while True:
            console.print("\n[bold blue]--- AIO Menu ---[/bold blue]")
            console.print("1. Generate a new temporary email")
            console.print("2. Check the email inbox for new messages (single email)")
            console.print("3. Generate multiple temporary emails (Spam Mode)")
            console.print("4. Start checking all spammed emails for messages (all emails)")
            console.print("5. Sign up all generated emails to Spotify")
            console.print("6. View Credits")
            console.print("7. Exit")

            choice = console.input("\n[bold green]Enter your choice: [/bold green]")

            if choice == '1':
                email = await get_temp_email(session)
                emails.append(email)
                console.print(f"[green]New temporary email generated: {email}[/green]")

            elif choice == '2':
                if emails:
                    console.print("[yellow]Checking email inbox for the last generated email...[/yellow]")
                    await check_email_inbox(session, emails[-1])
                else:
                    console.print("[red]No email address generated. Please generate one first.[/red]")

            elif choice == '3':
                num_emails = int(console.input("[bold green]Enter the number of emails to generate: [/bold green]"))
                console.print(f"[yellow]Generating {num_emails} emails...[/yellow]")
                new_emails = await spam_emails(session, num_emails)
                emails.extend(new_emails)
                console.print(f"[green]Generated {len(new_emails)} emails in total.[/green]")

            elif choice == '4':
                if emails:
                    console.print("[yellow]Starting to check all spammed emails for new messages...[/yellow]")
                    tasks = [check_email_inbox(session, email) for email in emails]
                    await asyncio.gather(*tasks)
                else:
                    console.print("[red]No spammed emails to check. Please generate some emails first using option 3.[/red]")

            elif choice == '5':
                if emails:
                    console.print(f"[yellow]Signing up {len(emails)} emails to Spotify...[/yellow]")
                    await signup_all_emails(emails)
                else:
                    console.print("[red]No emails to sign up. Please generate some emails first using option 3.[/red]")

            elif choice == '6':
                display_credits()

            elif choice == '7':
                console.print("[bold red]Exiting...[/bold red]")
                break

            else:
                console.print("[red]Invalid choice. Please try again.[/red]")

# Run the menu
asyncio.run(menu())
