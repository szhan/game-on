import argparse
import copy
import json
from io import StringIO


parser = argparse.ArgumentParser(description="Extract timeline data from a JSON file and dump into a CSV file.")
parser.add_argument('-i', '--in-file', type=str, dest='in_file', required=True, help='Input file with match timeline data in JSON')
parser.add_argument('-o', '--out-file', type=str, dest='out_file', required=True, help='Output file with match timeline data in CSV')
args = parser.parse_args()


IN_FILE = args.in_file
OUT_FILE = args.out_file


fh_csv = open(OUT_FILE, 'w')

# Print header
fh_csv.write(",".join([
			'gameId', 'timestamp', 'participantId', 'level',
			'totalGold', 'currentGold', 'xp', 'minionsKilled',
			'jungleMinionsKilled', 'positionX', 'positionY',
			'championKills', 'assists', 'deaths',
			'wardsPlaced', 'buildingKills', 'monsterKills',
			'dragonKills', 'heraldKills', 'baronKills'
			]) + "\n")

for line in [x.strip() for x in open(IN_FILE, 'r')]:
	[game_id, json_str] = line.split("\t")
	json_data = json.loads(json_str)
	
	for frame in json_data["frames"]:
		for player in range(1, 11):
			player_data = frame["participantFrames"][str(player)]
			
			# Position data missing in last frame (CHECK)
			if "position" not in player_data.keys():
				player_data["position"] = {"y": "NA", "x": "NA"}
			
			# Parse event data in dict, where key is participant id and value is count
			# TODO: Figure out what creatorId = 0 means...
			ini_key = range(0, 11)
			ini_val = [0] * 11
			
			kills = {k:v for k,v in zip(ini_key, ini_val)}
			assists = copy.copy(kills)
			deaths = copy.copy(kills)
			wards_placed = copy.copy(kills)
			building_kills = copy.copy(kills)
			monster_kills = copy.copy(kills)
			dragon_kills = copy.copy(kills)
			herald_kills = copy.copy(kills)
			baron_kills = copy.copy(kills)
			
			for event in frame["events"]:
				if event["type"] == "CHAMPION_KILL":
					kills[event["killerId"]] += 1
					kills[event["victimId"]] += 1
					for i in event["assistingParticipantIds"]:
						assists[i] += 1
				elif event["type"] == "WARD_PLACED":
					wards_placed[event["creatorId"]] += 1
				elif event["type"] == "BUILDING_KILL":
					building_kills[event["killerId"]] += 1
					# TODO: Check if this can be missing
					for i in event["assistingParticipantIds"]:
						building_kills[i] += 1
				elif event["type"] == "ELITE_MONSTER_KILL":
					# TODO: Add participants?
					monster_kills[event["killerId"]] += 1
					
					if event["monsterType"] == "DRAGON":
						dragon_kills[event["killerId"]] += 1
					elif event["monsterType"] == "RIFTHERALD":
						herald_kills[event["killerId"]] += 1
					elif event["monsterType"] == "BARON_NASHOR":
						baron_kills[event["killerId"]] += 1
			
			fh_csv.write(",".join(str(x)
						for x in [
							game_id,
							frame["timestamp"],
							player_data["participantId"],
							player_data["level"],
							player_data["totalGold"],
							player_data["currentGold"],
							player_data["xp"],
							player_data["minionsKilled"],
							player_data["jungleMinionsKilled"],
							player_data["position"]["x"],
							player_data["position"]["y"],
							kills[player],
							assists[player],
							deaths[player],
							wards_placed[player],
							building_kills[player],
							monster_kills[player],
							dragon_kills[player],
							herald_kills[player],
							baron_kills[player]
						]) + "\n")

fh_csv.close()

