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
        for var in self.domains:
            newset = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    newset.add(word)
            self.domains[var] = newset

        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        if not self.crossword.overlaps[x, y]:
            return False

        i, j = self.crossword.overlaps[x, y]

        change = False
        newset = set()
        for wordx in self.domains[x]:
            valid = False
            for wordy in self.domains[y]:
                if wordx[i] == wordy[j]:
                    valid = True
                    break

            if not valid:
                change = True
            else:
                newset.add(wordx)

        self.domains[x] = newset
        return change

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = []
            for var in self.domains:
                for n in self.crossword.neighbors(var):
                    arcs.append((var, n))

        while arcs:
            x, y = arcs[0]
            arcs = arcs[1:]

            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for n in self.crossword.neighbors(x):
                    if n not in self.domains[y]:
                        arcs.append((n, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check var and word length are the same
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False

        # check word assigned to each var is unique
        uniqueset = set()
        length = 0
        for var in assignment:
            uniqueset.add(assignment[var])
            if len(uniqueset) == length:
                return False
            else:
                length += 1

        # check if neighbours have no conflicts
        for var in assignment:
            for n in self.crossword.neighbors(var):
                if n in assignment and self.crossword.overlaps[var, n]:
                    i, j = self.crossword.overlaps[var, n]
                    if assignment[var][i] != assignment[n][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        ruleout = {}

        for word in self.domains[var]:
            ruleout[word] = 0
            for n in self.crossword.neighbors(var):
                if n not in assignment:
                    if self.crossword.overlaps[var, n]:
                        i, j = self.crossword.overlaps[var, n]
                        for wordn in self.domains[n]:
                            if word[i] != wordn[j]:
                                ruleout[word] += 1

        return sorted(ruleout, key=lambda x: ruleout[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        minvar = None
        mincount = None
        maxdegree = None

        for var in self.domains:
            if var not in assignment:
                count = len(self.domains[var])
                degree = len(self.crossword.neighbors(var))
                if not minvar:
                    minvar = var
                    mincount = count
                    maxdegree = degree
                elif count < mincount:
                    minvar = var
                    mincount = count
                    maxdegree = degree
                elif count == mincount and degree > maxdegree:
                    minvar = var
                    mincount = count
                    maxdegree = degree

        return minvar

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment

        unassigned = self.select_unassigned_variable(assignment)

        for word in self.order_domain_values(unassigned, assignment):
            new_ass = assignment.copy()
            new_ass[unassigned] = word

            if self.consistent(new_ass):
                output = self.backtrack(new_ass)

                if not output:
                    return output

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
