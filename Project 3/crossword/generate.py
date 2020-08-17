import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction ==
                                  Variable.DOWN else 0)
                j = variable.j + (k if direction ==
                                  Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype(
            "assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for item in self.domains[var].copy():
                if(not var.length == len(item)):
                    self.domains[var].remove(item)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # check to see if revisions are made, initially false
        revision_made = False

        # if the two given variables overlap
        if self.crossword.overlaps[x, y]:
            # extract what their overlap is
            (i, j) = self.crossword.overlaps[x, y]
            # iterate through domain of first given node
            for x_val in self.domains[x].copy():
                # iterate through second node domain
                valid = False
                for y_val in self.domains[y]:
                    # check to see if there is a value consistent with node 1
                    if(x_val[i] == y_val[j]):
                        valid = True
                # if there is no node consistent, remove from node 1 domain
                if(not valid):
                    self.domains[x].remove(x_val)
                    # mark a revision as being made
                    revision_made = True
        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # fill queue if void
        if arcs is None:
            arcs = []
            for var1 in self.crossword.variables:
                for var2 in self.crossword.neighbors(var1):
                    arcs.append((var1, var2))

        # while there is still stuff available in the queue
        while(not len(arcs) == 0):
            # deque the first item in the list
            x, y = arcs.pop(0)
            # check arc consistency
            if(self.revise(x, y)):
                # check that there's still valid solutions
                if(len(self.domains[x]) == 0):
                    return False
                # update queue to reflect changes in revise
                for neighbor in self.crossword.neighbors(x):
                    if(not neighbor == y):
                        arcs.append((neighbor, x))
        # baseline return True
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # if the length of assignments matches number of variables
        if(len(assignment) == len(self.crossword.variables)):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        seen_words = []
        # iterate through keys and vals
        for item in assignment.keys():
            val = assignment[item]
            # make sure word isn't used multiple times
            if(val in seen_words):
                return False
            # add word to seen words
            seen_words.append(val)
            # make sure word is same length as blank
            if(not item.length == len(assignment[item])):
                return False
            # iterate through variables intersecting this variable
            for intersect in self.crossword.neighbors(item):
                # see if neighbor in assignment
                if intersect in assignment:
                    # get what the overlap is
                    (x, y) = self.crossword.overlaps[item, intersect]
                    # make sure that overlap is valid
                    if(not assignment[item][x] == assignment[intersect][y]):
                        return False

        # baseline return True
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # TODO - actually implement this optimization

        tracker = {}
        for in_domain in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if(in_domain in self.domains[neighbor]):
                    count += 1
            tracker[in_domain] = count

        return sorted(tracker, key=tracker.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_domain = len(self.crossword.words)
        options = []
        for var in self.crossword.variables:
            if var not in assignment:
                if(len(self.domains[var]) < min_domain):
                    min_domain = len(self.domains[var])
                    options = []
                    options.append(var)

        if(len(options) > 1):
            max_neighbors = 0
            best_option = None
            for item in options:
                if(len(self.crossword.neighbors(item)) > max_neighbors):
                    max_neighbors = len(self.crossword.neighbors(item))
                    best_option = item
            return best_option

        else:
            return options[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if(self.consistent(assignment)):
                result = self.backtrack(assignment)
                if(result):
                    return result
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
