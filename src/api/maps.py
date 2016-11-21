import googlemaps as gm


# ((username, address,),[(otherusers,addresses)])
def sortByDist(user, otherUsers):
	maps =  gm.Client(key="AIzaSyBSZGhzoWEwa8UjPG5AA_-Yyf977w6kaSk")
	#def distance_matrix(client, origins, destinations,
	#                    mode=None, language=None, avoid=None, units=None,
	#                    departure_time=None, arrival_time=None, transit_mode=None,
	#                    transit_routing_preference=None, traffic_model=None):
	response = maps.distance_matrix(user[1], [x[1] for x in otherUsers])
	distances = [int(x['distance']['text'].split(" ")[0]) for x in  response['rows'][0]['elements']]
	nearByList =  [(otherUsers[x][0],otherUsers[x][1],distances[x]) for x in range(len(otherUsers))]
	nearByList.sort(key = lambda u: u[2])
	return nearByList