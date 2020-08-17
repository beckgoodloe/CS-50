import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    run_program()


def run_program():
    source = person_id_for_name(input("Name: "))
    if source is None:
        print("Person not found. Try again.")
        run_program()
    target = person_id_for_name(input("Name: "))
    if target is None:
        print("Person not found. Try again.")
        run_program()

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")
    run_program()


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # make sure that both of the actors are actually in movies
    if(len(people[source]["movies"]) == 0 or
       len(people[target]["movies"]) == 0):
        return None
    # create the original node based on user input
    start = Node(state=source, parent=None, action=None)
    test = neighbors_for_person(start.state)
    for i in test:
        movie, actor = i
        if(actor == 437):
            print(movie)

    # create a queue to store the frontier
    frontier = QueueFrontier()

    # add the start node
    frontier.add(start)

    # create two sets, one to store explored nodes, one for easy search
    # set() for backtracking through parents
    # list for just names to not double add actors to frontier
    explored = set()
    list_explored = []
    # as long as the frontier isnt empty
    while(not frontier.empty()):
        # remove state from frontier
        focus_node = frontier.remove()
        # add it to explored set and explored list
        explored.add(focus_node)
        list_explored.append(focus_node.state)
        # add neighbors to frontier
        for pair in neighbors_for_person(focus_node.state):
            # for each neighbor, extract movie and their name (id)
            movie, person = pair
            # if it's the person we're looking for, print out sequence
            if(person == target):
                print("FOUND: Generating List")
                # create a list to store the backtracking to source
                return_list = [(movie, person)]
                # as long as we're not at the source
                while focus_node.parent is not None:
                    # add that node
                    return_list.append(
                        (focus_node.action, focus_node.state))
                    # find the parent node and move up the search tree
                    for adult in explored:
                        if(adult.state == focus_node.parent):
                            focus_node = adult
                            break
                # reverse the list only if we didn't reverse the order
                return return_list[::-1]

            # if the person is not our target, make sure they arent already in
            # the frontier or the explored sets
            elif(not frontier.contains_state(person) and person
                 not in list_explored):
                # create a node for them and add to frontier
                node = Node(
                    state=person, parent=focus_node.state, action=movie)
                frontier.add(node)
    # if the frontier is empty, there is no solution from source to target
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
