import argparse
import copy
import json
from io import StringIO


parser = argparse.ArgumentParser(description="Extract timeline data from a JSON file and dump into a CSV file.")
parser.add_argument('-i', '--in-timeline-file', type=str, dest='in_timeline_file', required=True, help='Input file with match timeline data in JSON')
parser.add_argument('-e', '--in-endpoint-file', type=str, dest='in_endpoint_file', required=True, help='Input file with match endpoint data in JSON')
parser.add_argument('-o', '--out-file', type=str, dest='out_file', required=True, help='Output file with match timeline data in CSV')
args = parser.parse_args()


IN_TIMELINE_FILE = args.in_timeline_file
IN_ENDPOINT_FILE = args.in_endpoint_file
OUT_FILE = args.out_file


ENDPOINT_DATA = {}
for game_id, json_str in [x.strip().split("\t") for x in open(IN_ENDPOINT_FILE, 'r')]:
	"""
	Participant ids (ranging from 1 to 10) are used in match timeline data 
	instead of account id (unique player identifiers outside each game).
	Extract from the corresponding match endpoint data to find the mapping
	between in-game participant ids and account ids.
	"""
	participant_account_map = {}
	
	list_participant_identity_dto = json.loads(json_str)["participantIdentities"]
	for participant in list_participant_identity_dto:
		participant_id = participant["participantId"]	# In-game id
		account_id = participant["player"]["accountId"]
		participant_account_map[participant_id] = account_id
	
	ENDPOINT_DATA[game_id] = participant_account_map


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

for line in [x.strip() for x in open(IN_TIMELINE_FILE, 'r')]:
	[game_id, json_str] = line.split("\t")
	json_data = json.loads(json_str)
	endpoint_data = ENDPOINT_DATA[game_id]
	
	for frame in json_data["frames"]:
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
				deaths[event["victimId"]] += 1
				
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
		
		# Print game statistcs for each player in this frame interval
		for player in range(1, 11):
			player_data = frame["participantFrames"][str(player)]
			player_id = player_data["participantId"]	# Should be equal to 'player'
			
			# Position data missing in last frame
			# TODO: Check if this is true...
			if "position" not in player_data.keys():
				player_data["position"] = {"y": "NA", "x": "NA"}
			
			fh_csv.write(",".join(str(x)
						for x in [
							game_id,
							frame["timestamp"],
							endpoint_data[player_id],	# account id
							player_data["level"],
							player_data["totalGold"],
							player_data["currentGold"],
							player_data["xp"],
							player_data["minionsKilled"],
							player_data["jungleMinionsKilled"],
							player_data["position"]["x"],
							player_data["position"]["y"],
							kills[player_id],
							assists[player_id],
							deaths[player_id],
							wards_placed[player_id],
							building_kills[player_id],
							monster_kills[player_id],
							dragon_kills[player_id],
							herald_kills[player_id],
							baron_kills[player_id]
						]) + "\n")

fh_csv.close()

