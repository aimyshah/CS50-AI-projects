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
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
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
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
            words = self.domains[var].copy()
            for word in words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Variable to store if change was made or not
        revised = False

        # Variable to store overlap indices
        overlap = self.crossword.overlaps[(x, y)]

        # Lists of words in the domains of x and y
        x_words = self.domains[x].copy()
        y_words = self.domains[y].copy()

        if overlap is None:
            return revised
        else:
            # List of letters at the overlap positions considering words in y_words
            y_letters = [word[overlap[1]] for word in y_words]

            # check if each value word in x's domain leaves possible words for y without a conflict
            for x_word in x_words:
                if x_word[overlap[0]] in y_letters:
                    continue
                else:
                    self.domains[x].remove(x_word)
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = []
            for arc in self.crossword.overlaps.keys():
                if self.crossword.overlaps[arc] is not None:
                    queue.append(arc)

        else:
            queue = arcs.copy()

        while len(queue) != 0:
            x, y = queue.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in (self.crossword.neighbors(x) - {y}):
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var in assignment:
                continue
            else:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        for var in assignment.keys():
            if len(assignment[var]) != var.length:
                return False
            for var2 in self.crossword.neighbors(var):
                i, j = self.crossword.overlaps[(var, var2)]
                if var2 in assignment:
                    if assignment[var][i] != assignment[var2][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Variable to store the number of values ruled out for each word in the domain of var
        ruled = dict()

        # Add the word and the corresponding number of words ruled out from neighbors in the dictionary
        for word_var in self.domains[var]:
            n = 0
            for var2 in self.crossword.neighbors(var):
                if var2 not in assignment:
                    i, j = self.crossword.overlaps[(var, var2)]
                    for word_var2 in self.domains[var2]:
                        if word_var[i] != word_var2[j]:
                            n += 1
            ruled[word_var] = n

        # Sort words in the domain of var
        ordered = sorted(ruled.items(), key=lambda x: x[1])
        domain = [x[0] for x in ordered]

        return domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Initialize an empty list to keep track of the properties of var as tuples
        # Each tuple represents: variable, number of words, number of neighbors
        var_properties_list = []

        # Add tuples for each not assigned variable
        for var in self.domains.keys():
            if var not in assignment:
                domain_len = len(self.domains[var])
                neighbors_len = len(self.crossword.neighbors(var))
                var_properties_list.append((var, domain_len, neighbors_len))

        # Sort the properties list considering the number of neighbors and words
        sorted_list = sorted(var_properties_list, key=lambda x: (x[1], x[2]))

        return sorted_list[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Checks if the assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Loop through all the words in the domain of the word selected
        for word in self.order_domain_values(var, assignment):

            # Create a copy of the assignment dictionary to avoid alterations
            new_assignment = assignment.copy()

            # Add the new assignment to the dictionary copied
            new_assignment[var] = word

            # If the assignment is consistent.Add the assignment to the original dictionary
            # Enforce arc consistency and call backtrack
            if self.consistent(new_assignment):
                assignment[var] = word
                arcs = [(x, var) for x in self.crossword.neighbors(var)]
                self.ac3(arcs)
                result = self.backtrack(assignment)
                if result is not None:
                    return result

            # Delete the assignment if not consistent
            delete = assignment.pop(var, None)

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
