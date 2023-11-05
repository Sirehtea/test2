import sys
import json
from ping3 import ping
import time
from bs4 import BeautifulSoup
import os
import threading
from rich import print

if not os.path.exists("reports"):
    os.makedirs("reports")

def save_servers_to_json(servers):
    with open("servers.json", "w") as file:
        json.dump(servers, file)

def load_servers_from_json():
    servers = {}
    try:
        with open("servers.json", "r") as file:
            servers = json.load(file)
    except FileNotFoundError:
        pass
    return servers

servers_to_check = load_servers_from_json()

def ping_server(server):
    response_time = ping(server)
    status = {"timestamp": time.ctime(), "response_time": response_time} if response_time is not None else {"timestamp": time.ctime(), "response_time": None}
    if server in servers_to_check:
        servers_to_check[server]["checks"].append(status)
        save_servers_to_json(servers_to_check)
        update_monitoring_log(server, "online" if response_time is not None else "offline")

def add_server(server):
    servers_to_check[server] = {"checks": []}
    save_servers_to_json(servers_to_check)

def remove_server(server):
    if server in servers_to_check:
        del servers_to_check[server]
        save_servers_to_json(servers_to_check)

def list_servers():
    print("Lijst van gemonitorde servers:")
    for server in servers_to_check:
        print(server)

def save_logs_to_json(logs):
    with open("monitoring_log.json", "w") as file:
        json.dump(logs, file)

def load_logs_from_json():
    logs = []
    try:
        with open("monitoring_log.json", "r") as file:
            logs = json.load(file)
    except FileNotFoundError:
        pass
    return logs

def update_monitoring_log(server, status):
    logs = load_logs_from_json()
    timestamp = time.ctime()
    logs.append({"server": server, "status": status, "timestamp": timestamp})
    save_logs_to_json(logs)

def generate_html_report():
    monitoring_logs = load_logs_from_json()
    html_report = "<html><head><title>Monitoring Report</title><link rel=\"stylesheet\" href=\"reset.css\"><link rel=\"stylesheet\" href=\"stijl.css\"></head><body><h1>Monitoring Report</h1><div><ul>"

    for log in monitoring_logs:
        server = log["server"]
        status = log["status"]
        timestamp = log["timestamp"]

        css_class = ""
        if status == "online":
            css_class = "online"
        else:
            css_class = "offline"

        report_entry = f"<li class=\"{css_class}\">Server: {server}, Status: {status}, Timestamp: {timestamp}</li>"
        html_report += report_entry

    html_report += "</ul></div></body></html>"

    with open("reports/monitoring_report.html", "w") as report_file:
        report_file.write(html_report)
        print("[bold green]HTML-rapport gegenereerd.[/bold green]")


def start_monitoring(interval):
    global monitoring_active

    def monitoring_task():
        while monitoring_active:
            for server in servers_to_check:
                ping_server(server)
            print(f"[bold green]Monitoring is actief. Volgende controle over [bold red]{interval} [/bold red]seconden...[/bold green]")
            generate_html_report() 
            time.sleep(interval)

    monitoring_active = True
    monitoring_thread = threading.Thread(target=monitoring_task)
    monitoring_thread.daemon = True
    monitoring_thread.start()

def stop_monitoring():
    global monitoring_active
    monitoring_active = False

def main_interactive():
    while True:
        print("-----------------------------------------------------------------")
        print("[italic magenta]CLI commando's\npython monitoring_script.py add_server <servernaam>\npython monitoring_script.py remove_server <servernaam>\npython monitoring_script.py list_servers\npython monitoring_script.py start_monitoring <interval>\npython monitoring_script.py stop_monitoring\n[/italic magenta]")
        print("[bold cyan]1. Voeg een server toe[/bold cyan]")
        print("[bold yellow]2. Verwijder een server[/bold yellow]")
        print("[bold green]3. Toon de lijst van servers[/bold green]")
        print("[bold cyan]4. Start monitoring[/bold cyan]")
        print("[bold yellow]5. Stop monitoring[/bold yellow]")
        print("[bold red]6. Exit[/bold red]")
        choice = input("Voer het nummer van de actie in: ")

        if choice == "1":
            server = input("Voer de servernaam of het IP-adres in om toe te voegen: ")
            add_server(server)
            print(f"[bold green]Server {server} is toegevoegd aan de lijst van servers.[/bold green]")
        elif choice == "2":
            server = input("Voer de servernaam of het IP-adres in om te verwijderen: ")
            remove_server(server)
            print(f"[bold red]Server {server} is verwijderd uit de lijst van servers.[/bold red]")
        elif choice == "3":
            list_servers()
        elif choice == "4":
            interval = int(input("Voer het controle-interval in seconden in: "))
            start_monitoring(interval)
        elif choice == "5":
            stop_monitoring()
            print("[yellow]Monitoring is gestopt.[/yellow]")
        elif choice == "6":
            break
        else:
            print("[bold red]Ongeldige keuze. Probeer opnieuw.[/bold red]")

def main_command_line():
    if len(sys.argv) < 2:
        print("[bold red]Gebruik: python monitoring_script.py add_server <servernaam> / remove_server <servernaam> / list_servers / start_monitoring/ stop monitoring[/bold red]")
        return

    action = sys.argv[1]

    if action == "add_server":
        if len(sys.argv) == 3:
            add_server(sys.argv[2])
        else:
            print("[bold red]Gebruik: python monitoring_script.py add_server <servernaam>[/bold red]")
    elif action == "remove_server":
        if len(sys.argv) == 3:
            remove_server(sys.argv[2])
        else:
            print("[bold red]Gebruik: python monitoring_script.py remove_server <servernaam>[/bold red]")
    elif action == "list_servers":
        list_servers()
    elif action == "start_monitoring":
        if len(sys.argv) == 3:
            interval = int(sys.argv[2])
            print("OK")
            start_monitoring(interval)
    elif action == "stop_monitoring":
            stop_monitoring()
    else:
        print("[bold red]Ongeldige actie. Gebruik: python monitoring_script.py add_server <servernaam> / remove_server <servernaam> / list_servers / start_monitoring / stop_monitoring![/bold red]")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_command_line()
    else:
        main_interactive()
