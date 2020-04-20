from utils import *
import time


t0 = time.clock()
iteration = 0

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[''.join(e) for e in zip('ABCDEFGHI', '123456789')],[''.join(e) for e in zip('ABCDEFGHI', '987654321')]]
unitlist = row_units + column_units + square_units + diagonal_units

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)



def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    # TODO: Implement this function!
    for unit in unitlist:
        nakedtwins = get_unit_naked_twins(unit, values, 2)
        eliminate_naked_twins_from_peers(unit, values, nakedtwins)
    return values

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for box in [i for i in values.keys() if len(values[i]) == 1]:
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(values[box], ''), 'eliminate', time.clock() - t0, iteration)
            #values[peer] = values[peer].replace(values[box], '')
    return values

def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit, 'only_choice', time.clock() - t0, iteration)
                #values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:

        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        
        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Naked Twins Strategy
        #values = naked_twins(values)    

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        
        if solved_values_after == 81:
            break
        
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """      
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values    
    n,s = min([(len(values[s]), s, ) for s in boxes if len(values[s]) > 1])
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            global iteration  
            iteration = iteration + 1
            return attempt

def get_unit_naked_twins(unit, values, length):
    inv_dict = {}
    boxes = { k: values[k] for k in unit }        
    inv_dict = {} 
    for key, value in boxes.items():
        if len(value) == length: 
            inv_dict.setdefault(value, set()).add(key)
    return [( list(inv_dict[key]), key ) for key, values in inv_dict.items() if len(values) > 1]

def eliminate_naked_twins_from_peers(unit, values, nakedtwins):
    if len(nakedtwins) > 0:
        for twin in nakedtwins:
            for box in ([e for e in unit if e not in twin[0] and len(values[e]) > 1]):
                for digit in twin[1]:
                    assign_value(values, box, values[box].replace(digit, ''), 'naked_twins', time.clock() - t0, iteration)
                    #values[box] = values[box].replace(digit, '')


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)

    return values


def main():
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    #diag_sudoku_grid = '1......2.....9.5...............8...4.........9..7123...........3....4.....936.4..'
    #diag_sudoku_grid = '...8...1.781..........1....4.......5..8..7.....75.319................6.........3.'
    display(grid2values(diag_sudoku_grid))
    print('/n===================================================/n')
    result = solve(diag_sudoku_grid)
    display(result)

    display(grid2values('9614527838359762412748135691472389.658376941.6291458373526.71.44965213787183.46..'))


    #display(grid2values('961324785835176249274..5361..7.38...583469172..975183.3.26.75.8796..24.31.8..36.7'))

    #print([ (e[1], e[2], e[3], e[4]) for e in history.values() if (e[1][0] == 'D4' or e[1][0] == 'I9') and e[1][1] == '2'])
    # print(sorted([e for e in history.values()], key=lambda tup: tup[3]))
    print(history)

    # try:
    #     import PySudoku
    #     PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    # except SystemExit:
    #     pass
    # except:
    #     print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')


if __name__ == "__main__":
    main()