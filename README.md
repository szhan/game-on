# game-on

This repo contains very lightweight wrappers to the Riot Games API. It supports only version 3, as version 2 is about to be deprecated at the time of coding. The full documentation of the API is here: https://developer.riotgames.com/.

It is assumed that a file named 'API_KEY', which contains the user API key, is in the main directory.


## Scripts
1. To download ranked game data for a specified league from a specified region.
```javascript
usage: fetch_ranked_game_data.py  [-h] [-l LEAGUE] -r REGION [-q QUEUE_TYPE]
				[-m MAX_REQUESTS_PER_MIN] [-n NBR_PLAYERS]
				[-g NBR_GAMES] [-o OUT_DIR] [-t TIME_GAP] [-d]

e.g.,
	python scripts/fetch_ranked_game_data.py -l CHALLENGER -r NA1 -n 20 -g 20
```

2. To convert timeline data in JSON to CSV
```javascript
usage: extract_timeline_data.py [-h] -i IN_TIMELINE_FILE -e IN_ENDPOINT_FILE -o OUT_FILE

e.g.,
	python scripts/extract_timeline_data.py -i data/challengers-timelines-BR1-RANKED_SOLO_5x5-2017_06_23.json
						-e data/challengers-endpoints-BR1-RANKED_SOLO_5x5-2017_06_23.json
						-o data/challengers-timelines-BR1-RANKED_SOLO_5x5-2017_06_23.csv
```


## Files
### Description of the JSON files
Running 'fetch_ranked_game_data.py' should yield four files containing the following types of data:
1. endpoints, i.e., victory versus defeat and final performance characteristics of each player (e.g., gold accumulated and total champion kills)
2. timelines, i.e., performance characteristics of each player over time (one minute intervals in epoch time) and event data (e.g., team fights and ward placement)
3. summoners, i.e., general information about a player's game account (e.g., account id and league points)
4. matchlist, i.e., match history of each player, as far back as available
```javascript
e.g., Challenger ranked solo queue 5x5 game data retrieved from the NA1 server...
	data/challengers-endpoints-NA1-RANKED_SOLO_5x5-2017_06_23.json
	data/challengers-timelines-NA1-RANKED_SOLO_5x5-2017_06_23.json
	data/challengers-summoners-NA1-RANKED_SOLO_5x5-2017_06_23.json
	data/challengers-matchlist-NA1-RANKED_SOLO_5x5-2017_06_23.json
```


### Description of the CSV files
The CSV files generated using 'extract_timeline_data.py' assembles timeline data from a bunch of matches. The files contain the following fields:
```javascript
1. gameId - unique match id
2. gameDuration - length of the match in epoch time (~60,000 units are equal to one minute)
3. timestamp - epoch time of the end of the time interval
4. accountId - unique player id
5. teamId - 100 or 200
6. win - game outcome (Win or Fail)
7. totalGold - total gold accumulated of the player by the end of the interval (EOI)
8. currentGold - current available (unspent) gold of the player by EOI
9. level - champion level of the player by EOI
10. xp - total experience gained of the player by EOI
11. minionsKilled - regular minions killed by the player by EOI
12. jungleMinionsKilled - jungle minions killed by the player by EOI
13. positionX - player's horizontal coordinate on Summoner's Rift (from 0 to 14820) by EOI
14. positionY - player's vertical coordinate on Summoner's Rift (from 0 to 14881) by EOI
15. championKills - enemy champions killed through final blow by the player by EOI
16. assists - enemy champions killed through assist by the player by EOI
17. deaths - times the player died by EOI
18. wardsPlaced - wards used by the player by EOI
19. buildingKills - buildings destroyed by the player by EOI
20. monsterKills - elite monsters killed by the player by EOI (= dragonKills + heraldKills + baronKills)
21. dragonKills - Dragons killed by the player by EOI
22. heraldKills - Rift Heralds killed by the player by EOI
23. baronKills - Baron Nashors killed by the player by EOI
```


## Notes about DTOs
Data are packed into JSON strings in a hierarchical manner:
```javascript
MatchDto
	ParticipantIdentityDto		list[dto]
		PlayerDto
	TeamStatsDto			list[dto]
		TeamBansDto		list[dto]
	ParticipantDto			list[dto]
		ParticipantStatsDto
		RuneDto			list[dto]
		ParticipantTimelineDto
		MasteryDto		list[dto]
```

```javascript
MatchTimelineDto
	MatchFrameDto			list[dto]
	MatchParticipantFrameDto	map[int,dto]
		MatchPositionDto
	MatchEventDto			list[dto]
```

MatchTimelineDto contains a list of MatchParticipantFrameDto ("participantFrames"),
e.g.,
```javascript
{
"participantFrames":
	{
	"1":{"participantId":1,"currentGold":377,"totalGold":8777,"level":14,"xp":11445,"minionsKilled":199,"jungleMinionsKilled":1},
	"2":{"participantId":2,"currentGold":233,"totalGold":6388,"level":11,"xp":7323,"minionsKilled":37,"jungleMinionsKilled":0},
	"3":{"participantId":3,"currentGold":1185,"totalGold":7985,"level":12,"xp":8826,"minionsKilled":20,"jungleMinionsKilled":84},
	"4":{"participantId":4,"currentGold":717,"totalGold":9642,"level":14,"xp":12376,"minionsKilled":227,"jungleMinionsKilled":12},
	"5":{"participantId":5,"currentGold":653,"totalGold":9903,"level":12,"xp":8769,"minionsKilled":200,"jungleMinionsKilled":1},
	"6":{"participantId":6,"currentGold":1061,"totalGold":10036,"level":14,"xp":12671,"minionsKilled":232,"jungleMinionsKilled":1},
	"7":{"participantId":7,"currentGold":673,"totalGold":10048,"level":13,"xp":10752,"minionsKilled":204,"jungleMinionsKilled":1},
	"8":{"participantId":8,"currentGold":144,"totalGold":7544,"level":11,"xp":7744,"minionsKilled":26,"jungleMinionsKilled":8},
	"9":{"participantId":9,"currentGold":1025,"totalGold":11275,"level":14,"xp":12844,"minionsKilled":29,"jungleMinionsKilled":165},
	"10":{"participantId":10,"currentGold":552,"totalGold":10077,"level":14,"xp":11854,"minionsKilled":194,"jungleMinionsKilled":3}
	},
	"events":
	[
	{"type":"WARD_PLACED","timestamp":1441294,"wardType":"YELLOW_TRINKET","creatorId":3},
	{"type":"WARD_PLACED","timestamp":1452236,"wardType":"YELLOW_TRINKET","creatorId":3},
	{"type":"WARD_PLACED","timestamp":1460124,"wardType":"UNDEFINED","creatorId":9},
	{"type":"BUILDING_KILL","timestamp":1460454,"position":{"x":1512,"y":6699},"killerId":10,"assistingParticipantIds":[6,7,8],"teamId":100,"buildingType":"TOWER_BUILDING","laneType":"TOP_LANE","towerType":"INNER_TURRET"},
	{"type":"WARD_PLACED","timestamp":1462373,"wardType":"SIGHT_WARD","creatorId":8},
	{"type":"WARD_KILL","timestamp":1464188,"wardType":"CONTROL_WARD","killerId":9},
	{"type":"SKILL_LEVEL_UP","timestamp":1464650,"participantId":1,"skillSlot":2,"levelUpType":"NORMAL"}
	],
	"timestamp":1500600
}
```

