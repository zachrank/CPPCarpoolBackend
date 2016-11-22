import googlemaps as gm
from api import db
from psycopg2.extras import DictCursor

def getNearbyUsers(user):
	    # lookup user
        c = db.cursor(cursor_factory=DictCursor)
        c.execute("SELECT * FROM users WHERE cppemail != %s", user)
        # check if we got a result
        users = []
        for i in range(c.rowcount()):
	        row = c.fetchone()
	        # shallow copy result
	        row = dict(row)
	        #get email and address
	        users.append((row['cppemail'],row['addressline1']))
	    return sortByDist(user,users)

# ((username, address,),[(otherusers,addresses)])
def sortByDist(user, otherUsers):
	nearByList = []
	for i in range(len(otherUsers)//25):
		nearByList.extend(getDists(user,otherUsers[i*25:(i+1)*25]))
	nearByList.extend(getDists(user,otherUsers[len(otherUsers) - (len(otherUsers) % 25):]))
	nearByList.sort(key = lambda u: u[2])
	return nearByList
#gmaps only takes 25 users at a time
def getDists(user, subUsers):
	maps =  gm.Client(key="AIzaSyBSZGhzoWEwa8UjPG5AA_-Yyf977w6kaSk")
	#def distance_matrix(client, origins, destinations,
	#                    mode=None, language=None, avoid=None, units=None,
	#                    departure_time=None, arrival_time=None, transit_mode=None,
	#                    transit_routing_preference=None, traffic_model=None):
	response = maps.distance_matrix(user[1], [x[1] for x in subUsers])
	#parse json
	distances = [int(x['distance']['text'].split(" ")[0]) for x in  response['rows'][0]['elements']]
	return [(subUsers[x][0],subUsers[x][1],distances[x]) for x in range(len(subUsers))]