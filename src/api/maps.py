import googlemaps as gm

# ((username, address,),[(otherusers,addresses)])
def sortByDist(user, otherUsers):
	nearByList = []
	for i in range(len(otherUsers)//25):
		nearByList.extend(getDists(user,otherUsers[i*25:(i+1)*25]))
	nearByList.extend(getDists(user,otherUsers[len(otherUsers) - (len(otherUsers) % 25):]))
	nearByList.sort(key = lambda u: u[1])
	return nearByList
#gmaps only takes 25 users at a time
def getDists(user, subUsers):
	maps =  gm.Client(key="AIzaSyBSZGhzoWEwa8UjPG5AA_-Yyf977w6kaSk")
	#def distance_matrix(client, origins, destinations,
	#                    mode=None, language=None, avoid=None, units=None,
	#                    departure_time=None, arrival_time=None, transit_mode=None,
	#                    transit_routing_preference=None, traffic_model=None):
	response = maps.distance_matrix(user[1], [x['addressline1'] for x in subUsers], units="imperial")
	#parse json
	distances = [x['distance']['text'].split(" ")[0] for x in  response['rows'][0]['elements']]
	return [(subUsers[x],distances[x]) for x in range(len(subUsers))]