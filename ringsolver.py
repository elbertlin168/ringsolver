#!/usr/bin/env python

import sys
import numpy as np

class RingSolver():

    def __init__(self, board, totalMoves):
        if board.shape[1] % 2 != 0:
            print('Board must have an even number of columns!')
            return
        self.board = np.copy(board)
        self.totalMoves = totalMoves

    def rotate(self, row, count):
        self.board[row] = np.roll(self.board[row], count)

    def slide(self, col, count):
        slyce = np.concatenate((self.board[:, col], self.board[::-1, (col + 6) % 12]))
        shift = np.roll(slyce, count)
        self.board[:, col] = shift[:4]
        self.board[::-1, (col + 6) % 12] = shift[4:]

    # TODO: make this work for boards where numEnemies % 8 != 0
    def isValid(self):
        check = np.copy(self.board)
        # Check full columns
        for col in range(check.shape[1]):
            if np.all(check[:, col]):
                check[:, col] = False
        # Check squares in bottom 2 rows
        for col in range(check.shape[1] - 1):
            if np.all(check[-2:, col:(col + 2)]):
                check[-2:, col:(col + 2)] = False
        # Check last square (wraps around)
        if np.all(check[-2:, 0]) and np.all(check[-2:, -1]):
            check[-2:, 0] = False
            check[-2:, -1] = False
        return not np.any(check)

    # TODO: prune symmetrical moves for SANIC SPEED
    def solve(self, moves):
        if self.isValid():
            return True, moves
        if len(moves) >= self.totalMoves:
            return False, moves

        # try rotations
        for i in range(self.board.shape[0]):
            # skip ring if no enemies to move
            if np.any(self.board[i]):
                for count in range(1, 12):
                    self.rotate(i, count)
                    solved, solution = self.solve(moves + [['r', chr(i + 65), count]])
                    if solved:
                        return solved, solution
                    self.rotate(i, -count)

        # try slides
        for j in range(self.board.shape[1] // 2):
            # skip slyce if no enemies to move
            if np.any(self.board[:, j]) or np.any(self.board[:, (j + 6) % 12]):
                for count in range(1, 8):
                    self.slide(j, count)
                    solved, solution = self.solve(moves + [['s', str(j), count]])
                    if solved:
                        return solved, solution
                    self.slide(j, -count)

        return False, moves
        
    def printMoves(self, moves):
        for move in moves:
            if move[0] == 'r':
                direction = 'right' if move[2] <= 6 else 'left'
                numMoves = 6 - abs(move[2] - 6)
                print('Rotate ring %s to the %s %i times' % (move[1], direction, numMoves))
            else:
                direction = 'down' if move[2] <= 4 else 'up'
                numMoves = 4 - abs(move[2] - 4)
                print('Slide slice %s %s %i times' % (move[1], direction, numMoves))

if __name__ == '__main__':
	print('Creating empty ring battle board of size 4x12...')
	board = np.zeros((4, 12), dtype=bool)

	# Input enemy coordinates
	enemyList = []
	while True:
		coordStr = input('Enter enemy coordinates, separated by a comma (type anything else to finish): ')
		coord = coordStr.split(',')
		if len(coord) != 2:
			break
		try:
			i = int(coord[0])
			j = int(coord[1])
			if i < 0 or i >= 4 or j < 0 or j >= 12:
				print('Invalid coordinates, try again')
				continue
			board[i, j] = True
			enemyList.append('(' + str(i) + ', ' + str(j) + ')')
			print('Adding enemy to coordinate ' + enemyList[-1])
		except:
			break
	print('Finished entering enemy coordinates. There are enemies at ' + ', '.join(enemyList))
	
	# Input total ring moves
	totalMovesStr = input('Enter number of ring moves: ')
	try:
		totalMoves = int(totalMovesStr)
	except:
		print('Invalid number of total moves, exiting')
		sys.exit(0)

	rs = RingSolver(board, totalMoves)
	print('Solving...')
	solved, solution = rs.solve([])
	if solved:
		print('Puzzle solution:')
		rs.printMoves(solution)
	else:
		print('Puzzle does not have a valid solution')
