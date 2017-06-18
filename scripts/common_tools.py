import time
import math
import pycurl
from datetime import date
from StringIO import StringIO


""" Simple utilities """
def get_api_key ():
	""" The file containing the API key is assumed to be in the main directory. """
	api_key_file = "../API_KEY"
	
	key = None
	with open(api_key_file) as file:
		key = file.read().rstrip()
	
	return key


def get_sleep_time(max_requests_per_min):
	time_gap = 2	# seconds
	return math.ceil(max_requests_per_min / 60.0) + time_gap


def get_formatted_date():
	""" Get current date YYYY-MM-DD as string. """
	return date.today().strftime("%Y_%m_%d")


""" Thin wrappers around Riot API (v3) """
def get_url_prefix(region_name):
	""" Create URL prefix, which is the Riot Game API website. """
	return "https://" + region_name + ".api.riotgames.com/lol"


def get_url_suffix(user_api_key):
	""" Create URL suffix for appending API key. """
	return "?api_key=" + user_api_key


def get_challengers_by_queue(url_prefix, url_suffix, queue_type):
	""" Use League v3 API call, and return LeagueListDTO. """
	return url_prefix + "/league/v3/challengerleagues/by-queue/" + queue_type + url_suffix


def get_masters_by_queue(url_prefix, url_suffix, queue_type):
	""" Use League v3 API call, and return LeagueListDTO. """
	return url_prefix + "/league/v3/masterleagues/by-queue/" + queue_type + url_suffix


def get_summoner_by_name(url_prefix, url_suffix, summoner_name):
	"""
	Use Summoner v3 API call, and return SummonerDTO. 
	Contents include 'name', 'id', and 'accountId', but see Riot API doc.
	WARNING: Use 'get_summoner_by_id' instead, because it is safer due to inconsistent encoding.
	"""
	return url_prefix + "/summoner/v3/summoners/by-name/" + summoner_name + url_suffix


def get_summoner_by_id(url_prefix, url_suffix, summoner_id):
	""" Use Summoner v3 API call, and return SummonerDTO. """
	return url_prefix + "/summoner/v3/summoners/" + str(summoner_id) + url_suffix


def get_match_list_by_account_id(url_prefix, url_suffix, account_id, recent=False):
	"""
	Use Match v3 API call, and return MatchlistDto, which contains a list of MatchReferenceDto.
	This return the full match history available, and data for each match is accessed via MatchReferenceDto.	
	Contents include 'matches' (list of MatchReferenceDto) and 'totalGames'.
	
	MatchReferenceDto contains 'lane', 'gameId', 'champion', 'role', but see Riot API doc.
	
	If recent set to True, then only data for the last 20 matches played are retrieved.
	"""
	if recent:
		return url_prefix + "/match/v3/matchlists/by-account/" + str(account_id) + "/recent" + url_suffix
	else:
		return url_prefix + "/match/v3/matchlists/by-account/" + str(account_id) + url_suffix


def get_match_endpoint_by_match_id(url_prefix, url_suffix, match_id):
	"""
	Use Match v3 API call, and return MatchDto, which contains multiple types of data:
	(1) ParticipantIdentityDto -> PlayerDto, (2) TeamStatsDto, and (3) ParticipantDto, and more.
	"""
	return url_prefix + "/match/v3/matches/" + str(match_id) + url_suffix


def get_match_timeline_by_match_id(url_prefix, url_suffix, match_id):
	"""
	Use Match v3 API call, and return MatchTimelineDto, which contains multiple types of data:
	(1) MatchFrameDto, (2) MatchParticipantFrameDto, (3) MatchEventDto, and more.
	"""
	return url_prefix + "/match/v3/timelines/by-match/" + str(match_id) + url_suffix


def get_json_by_request(api_cmd, max_attempts=5, sleep_time=3):
	""" Send request to Riot API server, and handle response, retrying requests up to a specified number of times. """
	json_data = None
	nbr_attempts = 0
	
	buffer = StringIO()
	c = pycurl.Curl()
	
	while True:
		c.setopt(c.URL, api_cmd)
		c.setopt(c.WRITEDATA, buffer)
		c.perform()
		
		""" Retry until successful. Not entirely sure if 0 is really the expected response... """
		resp_code = c.getinfo(c.RESPONSE_CODE)
		if resp_code == 200:
			""" Do something with response body """
			break
		elif resp_code in [400, 429]:
			print "ERROR: Bad request\n" + api_cmd + "\nExiting..."
			break
		elif resp_code == 403:
			print "ERROR: Rate limit violated! Check with Riot! Exiting..."
			break
		elif resp_code in [500, 503]:
			print "ERROR: Riot API server is down or unable to fulfill request. Exiting..."
			break
		elif resp_code == 429:
			""" Service could have been temporarily unavailable. Retry. """
		else:
			print "ERROR: Unrecognized HTTP response code " + resp_code + ". Exiting..."
			break
		
		nbr_attempts += 1
		if nbr_attempts >= max_attempts:
			break
		
		time.sleep(sleep_time)
	
	c.close()
	
	json_data = buffer.getvalue()
	
	return json_data


