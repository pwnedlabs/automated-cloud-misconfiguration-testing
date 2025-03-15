import json
import requests
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_gcp_perms():
    """Loads valid GCP permissions from a JSON file."""
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

def fetch_app_engine_versions(project_id, service_name, headers):
    """Fetches all versions for a given App Engine service and extracts config details."""
    url = f"https://appengine.googleapis.com/v1/apps/{project_id}/services/{service_name}/versions"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        versions = response.json().get("versions", [])
        service_details = []
        
        for version in versions:
            version_id = version.get("id", "Unknown")
            runtime = version.get("runtime", "Unknown")
            service_account = version.get("serviceAccount", "No service account found")
            env_variables = version.get("envVariables", {})
            #print(json.dumps(version, indent=2)) # Print the full version object
            #print(env_variables)

            service_details.append({
                "version_id": version_id,
                "runtime": runtime,
                "service_account": service_account,
                "env_vars": env_variables
            })
        
        return service_details
    else:
        return f"Error: {response.status_code} - {response.text}"

def check_app_engine_services(access_token, project_id):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    app_engine_perm = "appengine.services.list"
    valid_perms = load_gcp_perms()

    if app_engine_perm in valid_perms:
        app_engine_url = f"https://appengine.googleapis.com/v1/apps/{project_id}/services"
        response = requests.get(app_engine_url, headers=headers)
        print(response.json())
        if response.status_code == 200:
            services = response.json().get("services", [])
            table_data = []

            for service in services:
                service_name = service.get("id", "Unknown")
                service_versions = fetch_app_engine_versions(project_id, service_name, headers)

                if isinstance(service_versions, str):  # Handle API error
                    print(Fore.RED + service_versions + Style.RESET_ALL)
                    continue

                for version in service_versions:
                    service_account_display = (
                        Fore.RED if version["service_account"].endswith("@appspot.gserviceaccount.com") else Fore.YELLOW
                    ) + version["service_account"] + Style.RESET_ALL

                    env_vars_display = (
                        Fore.MAGENTA + json.dumps(version["env_vars"], indent=2)[:100] + "..." + Style.RESET_ALL
                        if version["env_vars"] else Fore.MAGENTA + "Unable to find the environment variable accurately" + Style.RESET_ALL
                    )

                    warning = (
                        Fore.RED + "⚠ Default service account detected!" + Style.RESET_ALL
                        if version["service_account"].endswith("@appspot.gserviceaccount.com")
                        else ""
                    )

                    table_data.append([
                        Fore.CYAN + service_name + Style.RESET_ALL,
                        Fore.BLUE + version["version_id"] + Style.RESET_ALL,
                        Fore.GREEN + version["runtime"] + Style.RESET_ALL,
                        service_account_display,
                        env_vars_display,
                        warning
                    ])

            headers = [
                Fore.WHITE + "Service Name" + Style.RESET_ALL,
                Fore.WHITE + "Version" + Style.RESET_ALL,
                Fore.WHITE + "Runtime" + Style.RESET_ALL,
                Fore.WHITE + "Service Account" + Style.RESET_ALL,
                Fore.WHITE + "Environment Variables" + Style.RESET_ALL,
                Fore.WHITE + "Warnings" + Style.RESET_ALL
            ]

            print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

        else:
            print(Fore.RED + f"App Engine API Error: {response.status_code} - {response.text}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Missing permission: appengine.services.list" + Style.RESET_ALL)
