import argparse
import copy
import json
from io import StringIO


parser = argparse.ArgumentParser(description="Extract timeline data from a JSON file and dump into a CSV file.")
parser.add_argument('-i', '--in-timeline-file', type=str, dest='in_timeline_file', required=True, help='Input file with match timeline data in JSON')
parser.add_argument('-e', '--in-endpoint-file', type=str, dest='in_endpoint_file', required=True, help='Input file with match endpoint data in JSON')
parser.add_argument('-o', '--out-timeline-file', type=str, dest='out_timeline_file', required=True, help='Output file with match timeline data in CSV')
parser.add_argument('-f', '--out-endpoint-file', type=str, dest='out_endpoint_file', required=True, help='Output file with match endpoint data in CSV')
args = parser.parse_args()


IN_TIMELINE_FILE = args.in_timeline_file
IN_ENDPOINT_FILE = args.in_endpoint_file
OUT_TIMELINE_FILE = args.out_timeline_file
OUT_ENDPOINT_FILE = args.out_endpoint_file


ENDPOINT_DATA = {}	# Final performance characteristics of each player for each game
ACCOUNT_DATA = {}	# Account id
TEAM_DATA = {}		# Team id
DURATION_DATA = {}	# Game duration, "gameDuration" in MatchDto
OUTCOME_DATA = {}	# Win, "win" in TeamStatsDto


fh_endpoints = open(OUT_ENDPOINT_FILE, 'w')

fh_endpoints.write(",".join([
				### General
				"participantId", "totalScoreRank",
				"totalPlayerScore",	"objectivePlayerScore", "combatPlayerScore",
				"champLevel", "win", "assists", "deaths",
				"goldEarned", "goldSpent",
				### Offense
				"totalDamageDealt", "physicalDamageDealt", "magicDamageDealt", "trueDamageDealt",
				"totalDamageDealtToChampions", "physicalDamageDealtToChampions", "magicDamageDealtToChampions", "trueDamageDealtToChampions",
				"largestCriticalStrike", "totalTimeCrowdControlDealt", "timeCCingOthers",
				### Defense
				"longestTimeSpentLiving", "damageSelfMitigated",
				"totalDamageTaken", "physicalDamageTaken", "magicalDamageTaken", "trueDamageTaken",
				"totalHeal", "totalUnitsHealed",
				### Building damage
				"turretKills", "inhibitorKills",
				"damageDealtToTurrets", "damageDealtToObjectives",
				### Creep score
				"totalMinionsKilled", "neutralMinionsKilled", "neutralMinionsKilledTeamJungle", "neutralMinionsKilledEnemyJungle",
				### Kills
				"kills", "doubleKills", "tripleKills", "quadraKills", "pentaKills",
				"largestMultiKill", "killingSprees", "largestKillingSpree",
				### Vision
				"visionScore", "wardsPlaced", "wardsKilled", "sightWardsBoughtInGame", "visionWardsBoughtInGame"
				]) + "\n")

for game_id, json_str in [x.strip().split("\t") for x in open(IN_ENDPOINT_FILE, 'r')]:
	"""
	Participant ids (ranging from 1 to 10) are used in match timeline data 
	instead of account id (unique player identifiers outside each game).
	
	Extract from the corresponding match endpoint data to find the mapping
	between in-game participant ids and account ids/team ids/game duration/win.
	"""
	json_data = json.loads(json_str)
	
	participant_endpoint_map = {}	# Dict within dict, game_id to player id to features
	participant_account_map = {}	# Map participant id to account id
	participant_team_map = {}	# Map participant id to team id
	team_outcome_map = {}		# Map team id to win
	
	list_participant_identity_dto = json_data["participantIdentities"]
	for participant in list_participant_identity_dto:
		participant_id = participant["participantId"]
		account_id = participant["player"]["accountId"]
		participant_account_map[participant_id] = account_id
	
	list_participant_dto = json_data["participants"]
	for participant in list_participant_dto:
		participant_id = participant["participantId"]
		team_id = participant["teamId"]
		participant_team_map[participant_id] = team_id
		player_stats = participant["stats"]
		fh_endpoints.write(",".join(str(x)
					for x in [
						### General
						player_stats["participantId"],
						player_stats["totalScoreRank"],
						player_stats["totalPlayerScore"],
						player_stats["objectivePlayerScore"],
						player_stats["combatPlayerScore"],
						#player_stats["teamObjective"],
						player_stats["champLevel"],
						player_stats["win"],
						player_stats["assists"],
						player_stats["deaths"],
						player_stats["goldEarned"],
						player_stats["goldSpent"],
						### Offense
						player_stats["totalDamageDealt"],
						player_stats["physicalDamageDealt"],
						player_stats["magicDamageDealt"],
						player_stats["trueDamageDealt"],
						player_stats["totalDamageDealtToChampions"],
						player_stats["physicalDamageDealtToChampions"],
						player_stats["magicDamageDealtToChampions"],
						player_stats["trueDamageDealtToChampions"],
						player_stats["largestCriticalStrike"],
						player_stats["totalTimeCrowdControlDealt"],
						player_stats["timeCCingOthers"],
						### Defense
						player_stats["longestTimeSpentLiving"],
						player_stats["damageSelfMitigated"],
						player_stats["totalDamageTaken"],
						player_stats["physicalDamageTaken"],
						player_stats["magicalDamageTaken"],
						player_stats["trueDamageTaken"],
						player_stats["totalHeal"],
						player_stats["totalUnitsHealed"],
						### Building
						#player_stats["firstTowerKill"],
						#player_stats["firstTowerAssist"],
						#player_stats["firstInhibitorKill"],
						#player_stats["firstInhibitorAssist"],
						player_stats["turretKills"],
						player_stats["inhibitorKills"],
						player_stats["damageDealtToTurrets"],
						player_stats["damageDealtToObjectives"],
						### Minions
						player_stats["totalMinionsKilled"],
						player_stats["neutralMinionsKilled"],
						player_stats["neutralMinionsKilledTeamJungle"],
						player_stats["neutralMinionsKilledEnemyJungle"],
						### Kills
						#player_stats["firstBloodKill"],
						#player_stats["firstBloodAssist"],
						player_stats["kills"],
						player_stats["doubleKills"],
						player_stats["tripleKills"],
						player_stats["quadraKills"],
						player_stats["pentaKills"],
						player_stats["largestMultiKill"],
						player_stats["killingSprees"],
						player_stats["largestKillingSpree"],
						player_stats["visionScore"],
						player_stats["wardsPlaced"],
						player_stats["wardsKilled"],
						player_stats["sightWardsBoughtInGame"],
						player_stats["visionWardsBoughtInGame"]
						]) + "\n")
	
	list_team_stats_dto = json_data["teams"]
	for team in list_team_stats_dto:
		team_id = team["teamId"]
		win = team["win"]
		team_outcome_map[team_id] = win
	
	ACCOUNT_DATA[game_id] = participant_account_map
	TEAM_DATA[game_id] = participant_team_map
	DURATION_DATA[game_id] = json_data["gameDuration"]
	OUTCOME_DATA[game_id] = team_outcome_map

fh_endpoints.close()


fh_timelines = open(OUT_TIMELINE_FILE, 'w')

# Print header
fh_timelines.write(",".join([
				'gameId', 'gameDuration', 'timestamp',
				'accountId', 'teamId', 'win',
				'totalGold', 'currentGold', 'level', 'xp',
				'minionsKilled', 'jungleMinionsKilled',
				'positionX', 'positionY',
				'championKills', 'assists', 'deaths',
				'wardsPlaced', 'buildingKills', 'monsterKills',
				'dragonKills', 'heraldKills', 'baronKills'
				]) + "\n")

for line in [x.strip() for x in open(IN_TIMELINE_FILE, 'r')]:
	[game_id, json_str] = line.split("\t")
	json_data = json.loads(json_str)
	endpoint_data = ACCOUNT_DATA[game_id]
	team_data = TEAM_DATA[game_id]
	duration_data = DURATION_DATA[game_id]
	outcome_data = OUTCOME_DATA[game_id]
	
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
			
			fh_timelines.write(",".join(str(x)
						for x in [
								game_id,
								duration_data,
								frame["timestamp"],
								endpoint_data[player_id],		# account id
								team_data[player_id],			# team id
								outcome_data[team_data[player_id]],
								player_data["totalGold"],
								player_data["currentGold"],
								player_data["level"],
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

fh_timelines.close()

