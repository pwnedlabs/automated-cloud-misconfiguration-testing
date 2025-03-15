import json
import requests
import time
import os
from tabulate import tabulate
from colorama import Fore, Style, init

def fetch_gcp_users_roles(access_token, project_id, output_file="gcp_users_roles.json"):
    """Fetches IAM users, roles, and permissions in a GCP project and displays them in a table."""
    init(autoreset=True)
    
    def get_iam_policy():
        url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}:getIamPolicy"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json={})
        return response.json() if response.status_code == 200 else None
    
    def get_role_permissions(role_name):
        url = f"https://iam.googleapis.com/v1/{role_name}"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.get(url, headers=headers)
        return response.json().get("includedPermissions", []) if response.status_code == 200 else []
    
    print(Fore.CYAN + "Fetching IAM policy..." + Style.RESET_ALL)
    iam_policy = get_iam_policy()
    if not iam_policy:
        print(Fore.RED + "Failed to retrieve IAM policy." + Style.RESET_ALL)
        return
    
    print(Fore.YELLOW + "Extracting users, roles, and permissions..." + Style.RESET_ALL)
    user_roles = {}
    for binding in iam_policy.get("bindings", []):
        role = binding["role"]
        for member in binding.get("members", []):
            if member.startswith("user:") or member.startswith("serviceAccount:"):
                user_email = member.split(":")[1]
                if user_email not in user_roles:
                    user_roles[user_email] = {"roles": []}
                permissions = get_role_permissions(role)
                user_roles[user_email]["roles"].append({"role": role, "permissions": permissions})
                time.sleep(0.5)  # Avoid API rate limits
    
    with open(output_file, "w") as f:
        json.dump(user_roles, f, indent=4)
    
    table_data = []
    for user, details in user_roles.items():
        for role in details["roles"]:
            table_data.append([
                Fore.CYAN + user + Style.RESET_ALL,
                Fore.YELLOW + role["role"] + Style.RESET_ALL,
                Fore.GREEN + ", ".join(role["permissions"])[:50] + "..." + Style.RESET_ALL
            ])
    
    headers = [Fore.WHITE + "User/Service Account" + Style.RESET_ALL,
               Fore.WHITE + "Role" + Style.RESET_ALL,
               Fore.WHITE + "Permissions (truncated)" + Style.RESET_ALL]
    
    print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    print(Fore.GREEN + f"Data saved to {output_file}" + Style.RESET_ALL)
