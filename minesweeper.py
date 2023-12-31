import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    '''
    Under what circumstances do we really know if a cell contains a mine or not?
    1. if the length of the observing cells is equal to the count
    2. if count == 0
    '''
    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        if cell in self.cells:
            self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbor_cells(self, cell):
        full_board_cells = { (i, j) for i in range(self.width) for j in range(self.height) }
        
        i, j = cell
        nearby_cells = {
            (i-1, j-1),
            (i, j-1),
            (i+1, j-1),
            (i-1, j),
            (i+1, j),
            (i-1, j+1),
            (i, j+1),
            (i+1, j+1),
        }
        nearby_cells.discard(cell)
        nearby_cells.intersection_update(full_board_cells)
        
        return nearby_cells

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        # The function should mark the cell as one of the moves made in the game.
        self.moves_made.add(cell)
        
        # The function should mark the cell as a safe cell, updating any sentences that contain the cell as well.
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # The function should add a new sentence to the AI’s knowledge base, based on the value of cell and count, to indicate that count of the cell’s neighbors are mines. Be sure to only include cells whose state is still undetermined in the sentence.
        neighbor_cells = self.get_neighbor_cells(cell)
        s = Sentence(neighbor_cells, count)

        neighbor_mines = neighbor_cells.intersection(self.mines)
        for neighbor in neighbor_mines:
            s.mark_mine(neighbor)

        neighbor_safes = neighbor_mines.intersection(self.safes)
        for neighbor in neighbor_safes:
            s.mark_safe(neighbor)
        
        self.knowledge.append(s)

        # If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            self.mines = self.mines.union(known_mines)

            known_safes = sentence.known_safes()
            self.safes = self.safes.union(known_safes)

        for mine in self.mines:
            self.mark_mine(mine)
        
        for safe in self.safes:
            self.mark_safe(safe)

        # infer new sentences from current knowledge
        new_knowledge = self.knowledge[:]
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 and s1.cells.issubset(s2.cells):
                    infered_sentence = Sentence(cells=s2.cells-s1.cells, count=s2.count-s1.count)
                    already_in_knowledge = any([infered_sentence == s for s in self.knowledge])
                    if not already_in_knowledge:
                        new_knowledge.append(infered_sentence)

        self.knowledge = new_knowledge

        # after inferences are made, see if there're new known mines and safes
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            self.mines = self.mines.union(known_mines)

            known_safes = sentence.known_safes()
            self.safes = self.safes.union(known_safes)

        for mine in self.mines:
            self.mark_mine(mine)
        
        for safe in self.safes:
            self.mark_safe(safe)

        print(f'curr knowledge -> ', [str(s) for s in self.knowledge])      


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        not_moved_safe_moves = self.safes - self.moves_made
        if not not_moved_safe_moves:
            return None
        
        return random.choice(list(not_moved_safe_moves))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        full_board_cells = { (i, j) for i in range(self.width) for j in range(self.height) }
        moves_to_play = full_board_cells - self.moves_made - self.mines

        if not moves_to_play:
            return None
        
        return random.choice(list(moves_to_play))