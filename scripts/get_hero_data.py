import requests
import csv
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

hero_code_path = current_dir.parent / 'data' / 'epic7_hero_codes.csv'

# Define the endpoint URL
url = "https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json?_=1729486911319"

# Make a GET request to the endpoint
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Extract the English hero data
    heroes = data.get("en", [])
    
    # Create a list of tuples containing hero codes and their corresponding names
    hero_data = [(hero["code"], hero["name"]) for hero in heroes if hero["code"] != "c0001" and hero["code"] != "c1005"]
    
    # Define the CSV file path
    csv_file_path = hero_code_path
    
    # Write the data to a CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["code", "name"])  # Write header
        writer.writerows(hero_data)

    print(f"Hero data saved to {csv_file_path}")
else:
    print(f"Failed to fetch data: {response.status_code}")
