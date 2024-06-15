from dotenv import load_dotenv
import os, requests, json

load_dotenv()

API_KEY = os.getenv("API_KEY")
# match_id = "1-7caef5b0-d063-4855-b349-77800a27f6c4"


def get_match_id():
    match_url = input("Enter match URL: ")
    return match_url.split("/")[-1]


# # Load match_data.json
# with open("match_data.json", "r") as file:
#     match_data = json.load(file)

# # Load match_stats.json
# with open("match_stats.json", "r") as file:
#     match_stats = json.load(file)


def get_team_name(faction_id):
    for faction_key, faction_data in match_data["teams"].items():
        if faction_data["faction_id"] == faction_id:
            return faction_data["name"]
    return "Failed to get Team Name"


def get_map_name(map_id):
    for map_data in match_data["voting"]["map"]["entities"]:
        for map in map_data:
            if map_data["game_map_id"] == map_id:
                return map_data["name"]
    return "Failed to get Map Name"


def get_player_name(player_id):
    for faction_key, faction_data in match_data["teams"].items():
        for player_data in faction_data["roster"]:
            if player_data["player_id"] == player_id:
                return player_data["game_player_name"]
    # if we can't get the game player name, we call the player details API for it
    player_details = get_player_details(player_id, API_KEY)
    return player_details["games"]["ow2"]["game_player_name"]


def get_team_stats(team_index, map_index):
    team_stats = []

    for player_data in match_stats["rounds"][map_index]["teams"][team_index]["players"]:
        player_stats = {
            "name": get_player_name(player_data["player_id"]),
            "player_stats": player_data["player_stats"],
        }
        team_stats.append(player_stats)

    # sort the stats by role, then name to follow Tank/Damage/Damage/Support/Support
    role_order = {"Tank": 0, "Damage": 1, "Support": 2}

    sorted_players = sorted(
        team_stats, key=lambda x: (role_order[x["player_stats"]["Role"]], x["name"])
    )

    return sorted_players


def get_match_data(match_id, api_key):
    url = f"https://open.faceit.com/data/v4/matches/{match_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_match_stats(match_id, api_key):
    url = f"https://open.faceit.com/data/v4/matches/{match_id}/stats"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def get_player_details(player_id, api_key):
    url = f"https://open.faceit.com/data/v4/players/{player_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()


def generate_title(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]
    return f"{team1} vs. {team2} / {competition_name} / Post-Match Discussion"


def generate_header(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]

    print(f"###{competition_name}")
    print(f"[FACEIT Match Overview]({match_data['faceit_url']})\n")
    print("---")
    print(
        f"###{team1} {match_data['results']['score']['faction1']}-{match_data['results']['score']['faction2']} {team2}"
    )
    print("---")

    return


def generate_map_scores(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    team1_score = match_data["results"]["score"]["faction1"]
    team2_score = match_data["results"]["score"]["faction2"]
    map_scores_table = (
        f"|{team1}|{team1_score}-{team2_score}|{team2}|\n|--:|:--:|:--|\n"
    )

    maps = match_data["voting"]["map"]["entities"]
    picked_maps_ids = match_data["voting"]["map"]["pick"]
    picked_maps = [m["name"] for m in maps if m["game_map_id"] in picked_maps_ids]

    for i, result in enumerate(match_data["detailed_results"]):
        map_score = f"|{result['factions']['faction1']['score']}|{picked_maps[i]}|{result['factions']['faction2']['score']}|\n"
        map_scores_table += map_score

    return map_scores_table


def generate_map_scoreboards(match_stats):
    for i, round in enumerate(match_stats["rounds"]):
        map_name = get_map_name(round["round_stats"]["Map"])
        winner_name = get_team_name(round["round_stats"]["Winner"])
        print(f"###MAP {i+1}: {round['round_stats']['OW2 Mode']} - {map_name}  ")
        print(f"**Winner: {winner_name}** - {round['round_stats']['Score Summary']}\n")

        stats_header = "|E|A|D|K/D|DMG|H|MIT|"
        header = f"{get_team_name(round['teams'][0]['team_id'])}" + stats_header
        print(header)
        print("--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:")

        team1_stats = get_team_stats(0, i)
        for y in range(5):
            stats_row = (
                f"{team1_stats[y]['name']}|{team1_stats[y]['player_stats']['Eliminations']}|"
                f"{team1_stats[y]['player_stats']['Assists']}|{team1_stats[y]['player_stats']['Deaths']}|"
                f"{team1_stats[y]['player_stats']['K/D Ratio']}|{team1_stats[y]['player_stats']['Damage Dealt']}|"
                f"{team1_stats[y]['player_stats']['Healing Done']}|{team1_stats[y]['player_stats']['Damage Mitigated']}|"
            )
            print(stats_row)

        print("\n")
        header = f"{get_team_name(round['teams'][1]['team_id'])}" + stats_header
        print(header)
        print("--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:")

        team2_stats = get_team_stats(1, i)
        for y in range(5):
            stats_row = (
                f"{team2_stats[y]['name']}|{team2_stats[y]['player_stats']['Eliminations']}|"
                f"{team2_stats[y]['player_stats']['Assists']}|{team2_stats[y]['player_stats']['Deaths']}|"
                f"{team2_stats[y]['player_stats']['K/D Ratio']}|{team2_stats[y]['player_stats']['Damage Dealt']}|"
                f"{team2_stats[y]['player_stats']['Healing Done']}|{team2_stats[y]['player_stats']['Damage Mitigated']}|"
            )
            print(stats_row)

        print("---")

    return


match_id = get_match_id()
match_data = get_match_data(match_id, API_KEY)
match_stats = get_match_stats(match_id, API_KEY)
print(generate_title(match_data))
generate_header(match_data)
print(generate_map_scores(match_data))
generate_map_scoreboards(match_stats)
