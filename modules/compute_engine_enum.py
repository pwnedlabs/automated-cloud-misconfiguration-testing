import json
import requests
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_gcp_compute_perms():
    with open('valid-gcp-perms.json') as f:
        return json.load(f)

def parse_compute_engine_instances(response_json):
    """Extracts instance name, zone, service account, networking details, and metadata from API response."""
    instances = []

    for zone, details in response_json.get("items", {}).items():
        if "instances" in details:
            for instance in details["instances"]:
                instance_name = instance.get("name")
                instance_zone = instance.get("zone", "").split("/")[-1]  # Extract zone name
                service_accounts = [sa["email"] for sa in instance.get("serviceAccounts", [])] if "serviceAccounts" in instance else ["No service account"]

                # Detect if a default service account is used
                is_default_sa = any("@developer.gserviceaccount.com" in sa for sa in service_accounts)

                # Extract network details
                network_interfaces = instance.get("networkInterfaces", [])
                networks = []
                for interface in network_interfaces:
                    internal_ip = interface.get("networkIP", "No internal IP")
                    access_configs = interface.get("accessConfigs", [])
                    
                    # Extract external IP and NAT details
                    external_ips = [ac["natIP"] for ac in access_configs if "natIP" in ac]
                    nat_attached = bool(access_configs)

                    networks.append({
                        "internal_ip": internal_ip,
                        "external_ips": external_ips if external_ips else ["No external IP"],
                        "nat_attached": nat_attached
                    })

                # Extract custom metadata
                metadata_items = instance.get("metadata", {}).get("items", [])
                metadata = {item["key"]: item["value"] for item in metadata_items} if metadata_items else {"No custom metadata": "N/A"}

                instances.append({
                    "name": instance_name,
                    "zone": instance_zone,
                    "service_accounts": service_accounts,
                    "is_default_sa": is_default_sa,
                    "networking": networks,
                    "metadata": metadata
                })
    
    return instances

def check_compute_instance(access_token, project_id):
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Compute Engine - List VMs
    compute_engine_perm = "compute.instances.list"
    valid_perms = load_gcp_compute_perms()  # Load permissions
    if compute_engine_perm in valid_perms:
        compute_url = f"https://compute.googleapis.com/compute/v1/projects/{project_id}/aggregated/instances"
        compute_response = requests.get(compute_url, headers=headers)
        
        if compute_response.status_code == 200:
            parsed_instances = parse_compute_engine_instances(compute_response.json())
            print(Fore.CYAN + f"Compute Instance:")
            if parsed_instances:
                table_data = []
                for instance in parsed_instances:
                    for net in instance["networking"]:
                        service_account_display = (Fore.RED if instance["is_default_sa"] else Fore.YELLOW) + ", ".join(instance["service_accounts"]) + Style.RESET_ALL
                        warning = Fore.RED + "⚠ Default service account detected!" + Style.RESET_ALL if instance["is_default_sa"] else ""

                        table_data.append([
                            Fore.CYAN + instance["name"] + Style.RESET_ALL,
                            Fore.GREEN + instance["zone"] + Style.RESET_ALL,
                            service_account_display,
                            Fore.MAGENTA + net["internal_ip"] + Style.RESET_ALL,
                            Fore.RED + ", ".join(net["external_ips"]) + Style.RESET_ALL,
                            Fore.BLUE + ("Yes" if net["nat_attached"] else "No") + Style.RESET_ALL,
                            "\n".join([f"{key}: {value}" for key, value in instance["metadata"].items()]),
                            warning
                        ])
                
                headers = [Fore.WHITE + "Instance Name" + Style.RESET_ALL,
                           Fore.WHITE + "Zone" + Style.RESET_ALL,
                           Fore.WHITE + "Service Accounts" + Style.RESET_ALL,
                           Fore.WHITE + "Internal IP" + Style.RESET_ALL,
                           Fore.WHITE + "External IPs" + Style.RESET_ALL,
                           Fore.WHITE + "NAT Attached" + Style.RESET_ALL,
                           Fore.WHITE + "Metadata" + Style.RESET_ALL,
                           Fore.WHITE + "Warnings" + Style.RESET_ALL]
                
                print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            else:
                print(Fore.RED + "No Compute Engine instances found." + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Compute Engine API Error: {compute_response.status_code} - {compute_response.text}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Missing permission: compute.instances.list" + Style.RESET_ALL)
