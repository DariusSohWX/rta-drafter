import requests
import json
import csv
import os

FIRST_PICK_ORDER = [1, 4, 5, 8, 9]
SECOND_PICK_ORDER = [2, 3, 6, 7, 10]
SEASON_CODE = "pvp_rta_ss15"

# Define the CSV file path
CSV_FILE = "data/epic7_matches.csv"


def collect_battle_data(nick_no, world_code, lang="en"):
    """
    Collects battle data from the Epic7 API and writes it to a CSV file.
    Args:
        nick_no (str): The nickname number of the player.
        world_code (str): The world code for the game.
        lang (str, optional): The language code for the API response. Defaults to "en".
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If the API request fails.
    The function performs the following steps:
        1. Constructs the API endpoint URL with the provided parameters.
        2. Sends a POST request to the API endpoint.
        3. Checks if the request was successful (status code 200).
        4. Extracts the battle list from the API response.
        5. Writes the battle data to a CSV file, appending to it if it already exists.
        6. Each row in the CSV file contains information about the battle, including:
            - My team picks
            - Enemy team picks
            - My bans
            - Enemy bans
            - First pick team
            - Winner
    """

    # API endpoint
    base_url = "https://epic7.gg.onstove.com/gameApi/getBattleList"
    params = {
        "nick_no": nick_no,
        "world_code": world_code,
        "lang": lang,
        "season_code": ""
    }
    url = f"{base_url}?nick_no={params['nick_no']}&world_code={params['world_code']}&lang={params['lang']}&season_code={params['season_code']}"

    # Send POST request
    response = requests.post(url)

    # Check if request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Extract battles list
        battles = data.get("result_body", {}).get("battle_list", [])
        
        # Define the header for the CSV file
        header = ["my_team_picks", "enemy_team_picks", "my_bans", "enemy_bans", "first_pick_team", "winner"]
        
        # Determine if the file already exists
        file_exists = os.path.isfile(CSV_FILE)
        
        # Open the CSV file in append mode
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            
            # Write the header only if the file does not exist (new file)
            if not file_exists:
                writer.writeheader()

            # Loop through each battle to extract relevant information
            for battle in battles:
                match_data = {}
                
                # Determine which team got the first pick (my_team or enemy)
                first_pick_team = 'my_team' if any(
                    hero.get('first_pick') == 1 for hero in battle.get('my_deck', {}).get('hero_list', [])
                ) else 'enemy_team'
                match_data['first_pick_team'] = first_pick_team
                
                # Define the pick order for both teams based on first pick
                my_pick_order = FIRST_PICK_ORDER if first_pick_team == 'my_team' else SECOND_PICK_ORDER
                enemy_pick_order = SECOND_PICK_ORDER if first_pick_team == 'my_team' else FIRST_PICK_ORDER
                
                # Assign pick orders to my team and enemy team
                my_team_picks = [
                    {
                        'hero_code': hero.get('hero_code'),
                        'pick_order': my_pick_order[i] if i < len(my_pick_order) else None
                    }
                    for i, hero in enumerate(battle.get('my_deck', {}).get('hero_list', []))
                ]
                enemy_team_picks = [
                    {
                        'hero_code': hero.get('hero_code'),
                        'pick_order': enemy_pick_order[i] if i < len(enemy_pick_order) else None
                    }
                    for i, hero in enumerate(battle.get('enemy_deck', {}).get('hero_list', []))
                ]

                # Skip writing to CSV if either team has no hero picks
                if not my_team_picks or not enemy_team_picks:
                    continue  # Skip this iteration if no picks are present

                # Convert the picks into a string for easier reading in the CSV
                match_data['my_team_picks'] = json.dumps(my_team_picks)
                match_data['enemy_team_picks'] = json.dumps(enemy_team_picks)

                # Extract pre-banned heroes and convert them to strings
                match_data['my_bans'] = json.dumps(battle.get('my_deck', {}).get('preban_list', []))
                match_data['enemy_bans'] = json.dumps(battle.get('enemy_deck', {}).get('preban_list', []))

                # Extract the winner (1 means win, 0 means lose)
                match_data['winner'] = 'my_team' if battle.get('iswin') == 1 else 'enemy_team'

                # Write the match data to the CSV file
                writer.writerow(match_data)

        print(f"Data successfully written to {CSV_FILE}")
        
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


# Function to fetch ranking data and extract nick_no, world_code for the top n players
def fetch_and_collect_ranking_data(n=5):
    
    # API endpoint for ranking data
    ranking_url = f"https://epic7.gg.onstove.com/gameApi/getWorldUserRankingDetail?lang=en&season_code={SEASON_CODE}&world_code=all"
    response = requests.post(ranking_url)

    if response.status_code == 200:
        ranking_data = response.json()
        players = ranking_data.get("result_body", [])
        
        # Limit to the top n players
        top_players = players[:n]

        # Iterate over each player and collect their battle data
        for player in top_players:
            nick_no = player.get("nick_no")
            world_code = player.get("world_code")
            lang = "en"  # As specified in the request

            print(nick_no, world_code)
            
            # Call the function to collect battle data for each player
            collect_battle_data(nick_no, world_code, lang)
            
    else:
        print(f"Failed to retrieve ranking data. Status code: {response.status_code}")

# Example usage: Get data for the top 10 players
fetch_and_collect_ranking_data(1)
