import googlemaps as gm


# ((username, address,),[(otherusers,addresses)])
def sortByDist(user, otherUsers):
    nearByList = []
    for i in range(len(otherUsers) // 25):
        nearByList.extend(getDists(user, otherUsers[i * 25:(i + 1) * 25]))
    nearByList.extend(getDists(user, otherUsers[len(otherUsers) - (len(otherUsers) % 25):]))
    nearByList.sort(key=lambda u: u[1])
    return nearByList


# gmaps only takes 25 users at a time
def getDists(user, subUsers):
    # maps = gm.Client(key="AIzaSyBSZGhzoWEwa8UjPG5AA_-Yyf977w6kaSk")
    maps = gm.Client(key="AIzaSyBDFnkopSlI9WxUmYpAB4MWYQ7UZaxFsH8")
    # def distance_matrix(client, origins, destinations,
    #                    mode=None, language=None, avoid=None, units=None,
    #                    departure_time=None, arrival_time=None, transit_mode=None,
    #                    transit_routing_preference=None, traffic_model=None):
    response = maps.distance_matrix(buildAddress(user), [buildAddress(u) for u in subUsers], units="imperial")
    # parse json
    distances = []
    for x in response['rows'][0]['elements']:
        if 'distance' in x and 'value' in x['distance']:
            meters = x['distance']['value']
            distances.append(meters / 1609.34)
        else:
            distances.append(-1.0)

    return [(subUsers[x], distances[x]) for x in range(len(subUsers))]


def buildAddress(user):
    address = user['addressline1']
    if user['addressline2'] is not None:
        address += ' ' + user['addressline2']
    address += ', ' + user['city'] + ' ' + str(user['zip'])
    return address
