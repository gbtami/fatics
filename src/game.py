import random

import globals

from variant.variant_factory import variant_factory

(WHITE, BLACK) = range(2)
def opp(side):
    assert side in [WHITE, BLACK]
    return BLACK if side==WHITE else WHITE

def side_to_str(side):
    assert side in [WHITE, BLACK]
    return "white" if side==WHITE else "black"

def find_free_slot():
    """Find the first available game number."""
    # This is O(n) in the number of games, but it's simple and should
    # be more than efficient enough.
    i = 1
    while True:
        if not i in globals.games:
            return i
        i += 1

class Game(object):
    def __init__(self, offer):
        self.number = find_free_slot()
        globals.games[self.number] = self
        side = offer.side
        if side == None:
            side = self._pick_color(offer.player_a.user, offer.player_b.user)
        if side == WHITE:
            self.white = offer.player_a
            self.black = offer.player_b
        else:
            assert(side == BLACK)
            self.white = offer.player_b
            self.black = offer.player_a

        self.white.user.session.is_white = True
        self.black.user.session.is_white = False

        self.speed = offer.speed
        rated_str = 'rated' if offer.rated else 'unrated'
        if not offer.is_time_odds:
            time_str = '%d %d' % (self.white.time,self.white.inc)
        else:
            time_str = '%d %d %d %d' % (self.white.time,self.white.inc,self.blacck.time,self.black.inc)
        self.white_clock = self.white.time*60.0
        self.black_clock = self.black.time*60.0

        self.last_move_verbose = 'none'
        self.last_move_san = 'none'
        self.last_move_mins = 0
        self.last_move_secs = 0.0
        self.flip = False
        self.white.user.clock_is_ticking = False
        self.black.user.clock_is_ticking = False

        self.abort_offered = [False, False]
        self.draw_offered = [False, False]
        self.adjourn_offered = [False, False]
        self.pause_offered = [False, False]

        # Creating: GuestBEZD (0) admin (0) unrated blitz 2 12
        create_str = 'Creating: %s (%s) %s (%s) %s %s %s\n' % (self.white.user.name, self.white.rating, self.black.user.name, self.black.rating, rated_str, offer.variant_and_speed, time_str)
    
        self.white.user.write(create_str)
        self.black.user.write(create_str)

        self.variant = variant_factory.get(offer.variant_name, self)

        #print(self.variant.to_style12(self.white.user))
        self.white.user.send_board(self.variant)
        self.black.user.send_board(self.variant)

    def _pick_color(self, a, b): 
        return random.choice([WHITE, BLACK])

    def next_move(self):
        #print(self.variant.to_style12(self.white.user))
        if self.variant.pos.is_checkmate or self.variant.pos.is_stalemate or \
                self.variant.pos.is_draw_nomaterial:
            self.white.user.clock_is_ticking = False
            self.black.user.clock_is_ticking = False
        if self.variant.pos.half_moves > 1:
            if self.variant.get_turn() == WHITE:
                self.white.user.clock_is_ticking = True
            else:
                self.black.user.clock_is_ticking = True

        self.white.user.send_board(self.variant)
        self.black.user.send_board(self.variant)

        if self.variant.pos.is_checkmate:
            if self.variant.get_turn() == WHITE:
                self.result('%s checkmated' % self.white.user.name, '0-1')
            else:
                self.result('%s checkmated' % self.black.user.name, '1-0')
        elif self.variant.pos.is_stalemate:
            self.result('Game drawn by stalemate', '1/2-1/2')
        elif self.variant.pos.is_draw_nomaterial:
            self.result('Game drawn because neither player has mating material', '1/2-1/2')

    def get_user_side(self, user):
        if user == self.white.user:
            return True
        elif user == self.black.user:
            return False
        else:
            raise RuntimeError('Game.get_side(): got a non-player')

    def get_side_user(self, side):
        if side:
            return self.white.user
        else:
            return self.black.user
    
    def abort(self, msg):
        self.result(msg, '*')

    def result(self, msg, code):
        line = '\n{Game %d (%s vs. %s) %s} %s\n' % (self.number,
            self.white.user.name, self.black.user.name, msg, code)
        self.white.user.write(line)
        self.black.user.write(line)
        self.free()

    def free(self):
        del globals.games[self.number]
        del self.white.user.session.games[self.black.user.name]
        del self.black.user.session.games[self.white.user.name]

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
