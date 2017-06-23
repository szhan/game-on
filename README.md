# game-on

This repo contains very lightweight wrappers to the Riot Games API. It supports only version 3, as version 2 is about to be deprecated at the time of coding. The full documentation of the API is here: https://developer.riotgames.com/.

It is assumed that a file named 'API_KEY', which contains the user API key, is in the main directory.


## Scripts
1. To download Challenger ranked solo queue 5x5 game data from a specified region.
```javascript
usage: fetch_challenger_data.py [-h] -r REGION [-m MAX_REQUESTS_PER_MIN]

e.g.,
	python scripts/fetch_challenger_data.py -r NA1 -m 40
```

2. To convert timeline data in JSON to CSV
```javascript
usage: extract_timeline_data.py [-h] -i IN_FILE -o OUT_FILE

e.g.,
	python scripts/extract_timeline_data.py
```


## Notes about DTOs:
Data are packed into JSON strings in a hierarchical manner:
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

MatchTimelineDto
	MatchFrameDto			list[dto]
	MatchParticipantFrameDto	map[int,dto]
		MatchPositionDto
	MatchEventDto			list[dto]

"participantFrames",
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

## TODO list
1. Partition data into one file per game (maybe endpoint and timeline data for the same game together).

