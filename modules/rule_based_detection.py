import json
import yaml
import os

def load_permissions(json_file_path):
    """Loads permissions from the JSON file."""
    with open(json_file_path, 'r') as file:
        permissions = json.load(file)
    return permissions

def load_yaml_rule(yaml_file_path):
    """Loads the YAML rule from a YAML file."""
    with open(yaml_file_path, 'r') as file:
        yaml_rule = yaml.safe_load(file)
    return yaml_rule

def match_permissions(permissions, yaml_rule):
    """Matches permissions based on the user-defined YAML rule."""
    rule_conditions = yaml_rule['rules'][0]['conditions']
    description = yaml_rule['rules'][0].get('description', 'No description available')
    lab = yaml_rule['rules'][0].get('lab', 'No lab available')
    source = yaml_rule['rules'][0].get('source', 'No source available')
    matches = []
    
    for permission in permissions:
        for condition in rule_conditions:
            if condition in permission:
                matches.append(permission)
    
    return matches, description, lab, source

def process_rules_directory(permissions, rules_directory):
    """Processes all YAML files in the rules directory and saves the matched permissions."""
    all_matches = []  # Store all matches in this list
    
    for file_name in os.listdir(rules_directory):
        if file_name.endswith('.yaml'):
            yaml_file_path = os.path.join(rules_directory, file_name)
            yaml_rule = load_yaml_rule(yaml_file_path)
            
            matches, description, lab, source = match_permissions(permissions, yaml_rule)
            
            if matches:
                print(f"\033[1;31mMatches found in rule '{file_name}'\033[0m")  # Red bold
                print(f"\033[1;36mDescription: {description}\033[0m")  # Cyan bold
                print(f"\033[1;34mLab: {lab}\033[0m")  # Blue bold
                print(f"\033[1;34mSource: {source}\033[0m")  # Blue bold
                for match in matches:
                    print(f"\033[1;32mPermission: {match}\033[0m")  # Green bold
                print("\n")

                # Save matches in a dictionary
                all_matches.append({
                    'rule': file_name,
                    'description': description,
                    'lab': lab,
                    'source': source,
                    'permissions': matches
                })
            else:
                print(f"\033[1;33mNo matches found in rule '{file_name}'.\033[0m\n")  # Yellow bold

    # Save all matches to a JSON file
    if all_matches:
        with open('matches.json', 'w') as json_file:
            json.dump(all_matches, json_file, indent=4)
        print("\033[1;32mMatches saved to 'matches.json'.\033[0m")

def main():
    # Path to the JSON file
    json_file_path = '../valid-gcp-perms.json'
    # Directory containing the YAML rule files
    rules_directory = '../rules/'
    
    # Load permissions from the JSON file
    permissions = load_permissions(json_file_path)
    
    # Process all YAML files in the rules directory
    process_rules_directory(permissions, rules_directory)

if __name__ == "__main__":
    main()
