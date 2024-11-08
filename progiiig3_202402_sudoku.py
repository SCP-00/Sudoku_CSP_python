import os
import itertools as it
from collections import deque

def read_board(file_path):
    """Read the text file and create the board dictionary."""
    board = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) != 81:
            raise ValueError("The file must contain exactly 81 lines.")
        rows = 'ABCDEFGHI'
        columns = '123456789'
        for i, line in enumerate(lines):
            row = rows[i // 9]
            column = columns[i % 9]
            cell = row + column
            options = line.strip()
            board[cell] = set(options) if len(options) > 1 else {options}
    return board

def print_board(board):
    """Print the Sudoku board."""
    rows = 'ABCDEFGHI'
    columns = '123456789'
    for row in rows:
        for column in columns:
            cell = row + column
            print(''.join(board[cell]) if len(board[cell]) == 1 else '.', end=' ')
        print()

def naked_single(board, constraints):
    """Apply the naked single technique."""
    for const in constraints:
        for KeyVar in const:
            if len(board[KeyVar]) == 1:
                for KeyXDelete in const:
                    if KeyXDelete != KeyVar:
                        board[KeyXDelete].discard(next(iter(board[KeyVar])))

def hidden_single(board, constraints):
    """Apply the hidden single technique."""
    for const in constraints:
        for digit in '123456789':
            count = 0
            last_key = None
            for KeyVar in const:
                if digit in board[KeyVar]:
                    count += 1
                    last_key = KeyVar
            if count == 1:
                board[last_key] = {digit}

def ac3(board, constraints):
    """Implement the AC3 algorithm to reduce domains."""
    queue = deque([(Xi, Xj) for const in constraints for Xi in const for Xj in const if Xi != Xj])
    
    while queue:
        Xi, Xj = queue.popleft()
        if revise_arc_consistency(Xi, Xj, board):
            if len(board[Xi]) == 0:
                return False
            # We change the set of lists to simply iterate over the constraints
            for const in constraints:
                if Xi in const:
                    for Xk in const:
                        if Xk != Xi and Xk != Xj:
                            queue.append((Xk, Xi))
    return True

def revise_arc_consistency(Xi, Xj, board):
    """Check if Xi's domain can be reduced by removing inconsistent values with Xj."""
    removed = False
    for x in board[Xi].copy():
        if not any(x != y for y in board[Xj]):
            board[Xi].discard(x)
            removed = True
    return removed

def mrv(board):
    """MRV heuristic (minimum remaining values)."""
    return min((v for v in board if len(board[v]) > 1), key=lambda x: len(board[x]), default=None)

def degree_heuristic(board, constraints):
    """Degree heuristic: Select the variable involved in the most constraints."""
    return max((v for v in board if len(board[v]) > 1), key=lambda x: sum(1 for c in constraints if x in c), default=None)

def is_board_complete(board):
    """Check if the board is complete."""
    return all(len(board[var]) == 1 for var in board)

def solve(board, constraints, verbose=False):
    """Search for a solution to the Sudoku board using backtracking and heuristics."""
    if is_board_complete(board):
        return board
    
    var = mrv(board) or degree_heuristic(board, constraints)
    
    if not var:
        return None

    for value in board[var].copy():
        board_copy = {v: board[v].copy() for v in board}
        board_copy[var] = {value}

        if ac3(board_copy, constraints):
            if verbose:
                print(f"Assigning {value} to variable {var}")
            solution = solve(board_copy, constraints, verbose)
            if solution:
                return solution
    
    return None

def generate_constraints():
    """Generate the constraints for Sudoku."""
    rows = 'ABCDEFGHI'
    columns = '123456789'
    
    def group(boxes):
        return [tuple(box) for box in boxes]

    # Rows
    row_groups = group([[row + column for column in columns] for row in rows])
    # Columns
    column_groups = group([[row + column for row in rows] for column in columns])
    # 3x3 Boxes
    box_groups = group([[row + column for row in rows[i:i+3] for column in columns[j:j+3]] for i in range(0, 9, 3) for j in range(0, 9, 3)])
    
    return row_groups + column_groups + box_groups

def main():
    default_path = r'Board_impossible_SD9BJKIA.txt'
    file_path = input("Enter the path of the Sudoku file (or press Enter to use the default path): ")
    if not file_path:
        file_path = default_path

    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return

    board = read_board(file_path)
    constraints = generate_constraints()
    
    print("Initial board:")
    print_board(board)
    
    solution = solve(board, constraints, verbose=True)
    
    if solution:
        print("\nSolution found!")
        print_board(solution)
    else:
        print("\nNo solution found.")

if __name__ == "__main__":
    main()
