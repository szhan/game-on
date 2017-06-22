import json
from io import StringIO

in_file = "data/challengers-timelines-kr-RANKED_SOLO_5x5-2017_06_18.json"

# Print header
print ",".join([
		'gameId', 'timestamp', 'participantId', 'level',
		'totalGold', 'currentGold', 'xp', 'minionsKilled',
		'jungleMinionsKilled', 'positionX', 'positionY',
		'championKills', 'assists', 'deaths',
		'wardsPlaced', 'buildingKills', 'eliteMonsterKills'
		])

game_counter = 0	# Temporary until gameId is included

for line in [x.rstrip() for x in open(in_file, 'r')]:
	game_counter += 1
	
	json_data = json.loads(line)
	
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
			# TODO: Use deepcopy
			kills = {k:v for k,v in zip(ini_key, ini_val)}
			assists = {k:v for k,v in zip(ini_key, ini_val)}
			deaths = {k:v for k,v in zip(ini_key, ini_val)}
			wards_placed = {k:v for k,v in zip(ini_key, ini_val)}		# TODO: Differentiate ward type, e.g., yellow or pink
			building_kills = {k:v for k,v in zip(ini_key, ini_val)}		# TODO: Differentiate building type, e.g., turret or inhibitor
			elite_monster_kills = {k:v for k,v in zip(ini_key, ini_val)}	# TODO: Differentiate monster type, e.g., dragon or baron
			
			for event in frame["events"]:
				if event["type"] == "CHAMPION_KILL":
					kills[event["killerId"]] += 1
					kills[event["victimId"]] += 1
					for i in event["assistingParticipantIds"]:
						kills[i] += 1
				elif event["type"] == "WARD_PLACED":
					wards_placed[event["creatorId"]] += 1
				elif event["type"] == "BUILDING_KILL":
					building_kills[event["killerId"]] += 1
					# TODO: Check if this can be missing
					for i in event["assistingParticipantIds"]:
						building_kills[i] += 1
				elif event["type"] == "ELITE_MONSTER_KILL":
					# TODO: Add participants?
					elite_monster_kills[event["killerId"]] += 1
			
			print ",".join(str(x)
					for x in [
						game_counter,
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
						elite_monster_kills[player]
					])

