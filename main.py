#import

import random 

# exceptions


class BoardOutException(Exception):
    pass


class OccupiedCellException(Exception):
    pass


class AlreadyFiredException(Exception):
    pass


class ShipDestroyedException(Exception):
    pass


class GameOverException(Exception):
    pass


class BoardNotFillableException(Exception):
    pass


# inner logic

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f'{self.y} {self.x}'


class Ship:

    def __init__(self, x, y, length, is_vertical):
        self._dots = list()
        self.hits = length
        self.is_vertical = is_vertical
        for i in range(length):
            if is_vertical:
                self._dots.append(Dot(x, y + i))
            else:
                self._dots.append(Dot(x + i, y))

    @property
    def dots(self):
        return self._dots

    def take_hit(self):
        self.hits -= 1


class Board:

    def __init__(self, is_ai):
        self.field = [[[False, False] for i in range(6)] for i in range(6)]
        self.ships = list()
        self.occupied_dots = list()
        self.hid = is_ai

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot):
                raise BoardOutException
            if dot in self.occupied_dots:
                raise OccupiedCellException
        self.ships.append(ship)
        for dot in ship.dots:
            self.field[dot.y - 1][dot.x - 1][1] = True
        self.occupied_dots.extend(ship.dots)
        for dot in self.contour(ship):
            if dot not in self.occupied_dots:
                self.occupied_dots.append(dot)

    def contour(self, ship):
        dots = list()
        for dot in ship.dots:
            x = dot.x
            y = dot.y
            for i in range(3):
                cur_x = x - 1 + i
                for j in range(3):
                    cur_y = y - 1 + j
                    cur_dot = Dot(cur_x, cur_y)
                    if all([not self.out(cur_dot),
                            cur_dot not in dots,
                            cur_dot not in ship.dots]):
                        dots.append(cur_dot)
        return dots

    @staticmethod
    def out(dot):
        return not (0 < dot.x <= 6 and 0 < dot.y <= 6)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException
        if self.is_shut(dot):
            raise AlreadyFiredException
        self.field[dot.y - 1][dot.x - 1][0] = True
        if self.has_ship(dot):
            for i in range(len(self.ships)):
                cur_ship = self.ships[i]
                if dot in cur_ship.dots:
                    cur_ship.take_hit()
                    if not cur_ship.hits:
                        for _dot in self.contour(self.ships.pop(i)):
                            self.field[_dot.y - 1][_dot.x - 1][0] = True
                        if len(self.ships):
                            raise ShipDestroyedException
                        else:
                            raise GameOverException
            return True
        return False

    def has_ship(self, dot):
        return self.field[dot.y - 1][dot.x - 1][1]

    def is_shut(self, dot):
        return self.field[dot.y - 1][dot.x - 1][0]

    def print_field(self):
        unshut_ship = 'O' if self.hid else '\u25A0'
        print('  |1|2|3|4|5|6|')
        i = 1
        for row in self.field:
            print('', i, end='|')
            for cell in row:
                if all(cell):
                    print('X', end='|')
                elif cell[0]:
                    print('T', end='|')
                elif cell[1]:
                    print(unshut_ship, end='|')
                else:
                    print('O', end='|')
            print()
            i += 1


# outer logic


class Player:
    def __init__(self, enemy_board):
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                dot = self.ask()
            except Exception:
                print('???????????????????????? ????????, ?????????????? 2 ?????????? ???? 1 ???? 6')
                continue
            try:
                return self.enemy_board.shot(dot)
            except BoardOutException:
                print('???????????????????????? ????????, ?????????????? 2 ?????????? ???? 1 ???? 6')
            except AlreadyFiredException:
                print('?????????? ?????? ?????? ??????')


class User(Player):
    name = '??????????'
    win = ' !!! ???????????? !!!'
    
    def ask(self):
        turn_input = input('?????????????? ?????????? ???????????? ?? ?????????????? ?????????? ???????????? ').split()
        if turn_input[0].lower() == 'exit':
            raise KeyboardInterrupt
        if len(turn_input) != 2:
            raise ValueError
        return Dot(int(turn_input[1]), int(turn_input[0]))


class AI(Player):
    name = '??????????????????'
    win = ' !!!??????????????????!!!'
    moves = [Dot(i, j) for i in range(1, 7) for j in range(1, 7)]

    def ask(self):
        rand_turn = random.randint(0, len(self.moves)-1)
        dot = self.moves.pop(rand_turn)
        input(f'???????????????? ?????????????????? ?? {dot}')
        return dot


class Game:
    user_board = Board(False)
    enemy_board = Board(True)

    def __init__(self):

        while True:
            try:
                self.random_board(self.user_board)
            except BoardNotFillableException:
                self.user_board = Board(False)
                continue
            else:
                break
        while True:
            try:
                self.random_board(self.enemy_board)
            except BoardNotFillableException:
                self.enemy_board = Board(True)
                continue
            else:
                break
        self.user = User(self.enemy_board)
        self.ai = AI(self.user_board)

    def random_board(self, board):
        ships_count = [1, 2, 4]
        tries = 0
        for i in range(3):
            for j in range(ships_count[i]):
                while True:
                    if tries > 50:
                        raise BoardNotFillableException
                    try:
                        ship = self.rand_ship(3-i)
                        board.add_ship(ship)
                    except:
                        tries += 1
                        continue
                    else:
                        break

    @staticmethod
    def rand_ship(length):
        x, y = random.randint(1, 6), random.randint(1, 6)
        orient = bool(random.randint(0, 1))
        return Ship(x, y, length, orient)

    @staticmethod
    def greet():
        print(' **************')
        print(' *            *')
        print(' *  ??????????????   *')
        print(' *    ??????     *')
        print(' *            *')
        print(' **************')
        if input('?????? ???????????? ????????\n ?????????????? Enter.\n  ???????????? ??????????:\n ?????????? ???????????? \n ?? ?????????? ?????????????? \n ?????????? ????????????.\n  ?????? ???????????? \n ?????????????? "exit".\n').lower() == 'exit':
            raise KeyboardInterrupt

    def print_boards(self):
        print('???????? ????????????\n')
        self.user_board.print_field()
        print('\n???????? ??????????????????\n')
        self.enemy_board.print_field()

    def loop(self):
        turn = 0
        while True:
            current_player = self.user if turn % 2 == 0 else  self.ai
            print(f'?????? {current_player.name}??\n')
            self.print_boards()
            while True:
                try:
                    while current_player.move():
                        self.print_boards()
                        print(' !!! ?????????? !!!')
                    print(' !!!  ????????  !!!')
                    input()
                    break
                except ShipDestroyedException:
                    self.print_boards()
                    print(' !!! ???????? !!!')
                    continue
                except GameOverException:
                    self.print_boards()
                    input(current_player.win)
                    return None
                break
            turn += 1

    def start(self):
        self.greet()
        self.loop()


def main():
    game = Game()
    game.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

