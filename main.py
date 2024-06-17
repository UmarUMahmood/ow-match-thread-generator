import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)


# Utility function to fetch data from the API
def fetch_data_from_api(endpoint, api_key):
    url = f"https://open.faceit.com/data/v4/{endpoint}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# Data retrieval functions
def get_match_data(match_id, api_key):
    return fetch_data_from_api(f"matches/{match_id}", api_key)


def get_match_stats(match_id, api_key):
    return fetch_data_from_api(f"matches/{match_id}/stats", api_key)


def get_player_details(player_id, api_key):
    return fetch_data_from_api(f"players/{player_id}", api_key)


# Helper functions
def get_team_name(faction_id, match_data):
    return next(
        (
            team["name"]
            for team in match_data["teams"].values()
            if team["faction_id"] == faction_id
        ),
        "Failed to get Team Name",
    )


def get_map_name(map_id, match_data):
    return next(
        (
            map_entity["name"]
            for map_entity in match_data["voting"]["map"]["entities"]
            if map_entity["game_map_id"] == map_id
        ),
        "Failed to get Map Name",
    )


def get_player_name(player_id, match_data, api_key):
    for team in match_data["teams"].values():
        for player in team["roster"]:
            if player["player_id"] == player_id:
                return player["game_player_name"]
    return get_player_details(player_id, api_key)["games"]["ow2"]["game_player_name"]


def get_team_stats(team_index, map_index, match_stats, match_data, api_key):
    role_order = {"Tank": 0, "Damage": 1, "Support": 2}
    return sorted(
        [
            {
                "name": get_player_name(player_data["player_id"], match_data, api_key),
                "player_stats": player_data["player_stats"],
            }
            for player_data in match_stats["rounds"][map_index]["teams"][team_index][
                "players"
            ]
        ],
        key=lambda x: (role_order[x["player_stats"]["Role"]], x["name"]),
    )


# Report generation functions
def generate_title(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]
    return f"{team1} vs. {team2} / {competition_name} / Post-Match Discussion"


def generate_header(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]
    return (
        f"## {competition_name}\n\n"
        f"[FACEIT Match Overview]({match_data['faceit_url']})\n\n"
        "---\n\n"
        f"## {team1} {match_data['results']['score']['faction1']}-{match_data['results']['score']['faction2']} {team2}\n\n"
        "---\n"
    )


def generate_map_scores(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    team1_score = match_data["results"]["score"]["faction1"]
    team2_score = match_data["results"]["score"]["faction2"]
    map_scores_table = (
        f"|{team1}|{team1_score}-{team2_score}|{team2}|\n|--:|:--:|:--|\n"
    )
    picked_maps_ids = match_data["voting"]["map"]["pick"]
    picked_maps = [
        map_entity["name"]
        for map_entity in match_data["voting"]["map"]["entities"]
        if map_entity["game_map_id"] in picked_maps_ids
    ]
    for i, result in enumerate(match_data["detailed_results"]):
        map_score = f"|{result['factions']['faction1']['score']}|{picked_maps[i]}|{result['factions']['faction2']['score']}|\n"
        map_scores_table += map_score
    return map_scores_table


def generate_map_scoreboards(match_stats, match_data, api_key):
    scoreboards = ""
    for i, round_data in enumerate(match_stats["rounds"]):
        map_name = get_map_name(round_data["round_stats"]["Map"], match_data)
        winner_name = get_team_name(round_data["round_stats"]["Winner"], match_data)
        scoreboards += (
            f"### MAP {i+1}: {round_data['round_stats']['OW2 Mode']} - {map_name}\n"
            f"**Winner: {winner_name}** - {round_data['round_stats']['Score Summary']}\n\n"
        )
        for team_index in range(2):
            team_name = get_team_name(
                round_data["teams"][team_index]["team_id"], match_data
            )
            scoreboards += f"{team_name}|E|A|D|K/D|DMG|H|MIT|\n"
            scoreboards += "--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:\n"
            team_stats = get_team_stats(team_index, i, match_stats, match_data, api_key)
            for player in team_stats:
                scoreboards += (
                    f"{player['name']}|{player['player_stats']['Eliminations']}|"
                    f"{player['player_stats']['Assists']}|{player['player_stats']['Deaths']}|"
                    f"{player['player_stats']['K/D Ratio']}|{player['player_stats']['Damage Dealt']}|"
                    f"{player['player_stats']['Healing Done']}|{player['player_stats']['Damage Mitigated']}|\n"
                )
            scoreboards += "---\n"
    return scoreboards


def generate_report(match_id, api_key):
    match_data = get_match_data(match_id, api_key)
    match_stats = get_match_stats(match_id, api_key)
    report_title = generate_title(match_data)
    report = f"{report_title}\n\n{generate_header(match_data)}\n{generate_map_scores(match_data)}\n{generate_map_scoreboards(match_stats, match_data, api_key)}"
    safe_title = "".join(
        c if c.isalnum() or c in (" ", "_") else "_" for c in report_title
    ).replace(" ", "_")
    filename = f"{safe_title}.md"
    with open(filename, "w") as file:
        file.write(report)
    print(f"Report generated for match {match_id} as {filename}")


@app.route("/webhook", methods=["POST"])
def get_match_id_from_webhook():
    if request.headers.get("Security-Header-Name") == "Security-Header-Value":
        match_id = request.json["payload"]["id"]
        generate_report(match_id, API_KEY)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "unauthorized"}), 401


if __name__ == "__main__":
    app.run(debug=True, port=5000)
