# -*- coding: utf-8 -*-
# Copyright (C) 2010  Wil Mahan <wmahan+fatics@gmail.com>
#
# This file is part of FatICS.
#
# FatICS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FatICS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with FatICS.  If not, see <http://www.gnu.org/licenses/>.
#

from command import *
from .match_command import MatchMixin

import seek
import match

@ics_command('seek', 't')
class Seek(Command):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_('You are examining a game.\n'))
            else:
                conn.write(_('You are playing a game.\n'))
            return

        if len(conn.user.session.seeks) >= seek.LIMIT:
            conn.write(_('You can only have %d active seeks.\n') % seek.LIMIT)
            return

        try:
            s = seek.Seek(conn.user, args[0])
        except match.MatchError as e:
            conn.write(e[0])
            return

        # Check if the user has already posted the same seek.  It might be
        # more efficient to do this check as part of seek.find_matching()
        if s in seek.seeks.values():
            conn.write(_('You already have an active seek with the same parameters.\n'))
            return

        (auto_matches, manual_matches) = seek.find_matching(s)
        if auto_matches:
            ad = auto_matches[0]
            conn.write(_('Your seek matches one posted by %s.\n') %
                ad.a.name)
            ad.a.write_('Your seek matches one posted by %s.\n',
                (conn.user.name,))
            ad.b = conn.user
            g = game.PlayedGame(ad)
            return
        if manual_matches:
            conn.write(_('Issuing match request because seek was.\n' %
                ad.a.name))
            for ad in manual_matches:
                pass

        count = s.post()
        conn.write(_('Your seek has been posted with index %d.\n') % s.num)
        conn.write(ngettext('(%d player saw the seek.)\n',
            '(%d players saw the seek.)\n', count) % count)

@ics_command('unseek', 'p')
class Unseek(Command):
    def run(self, args, conn):
        n = args[0]
        if n:
            if n in seek.seeks and seek.seeks[n].a == conn.user:
                seek.seeks[n].remove()
                conn.write(_('Your seek %d has been removed.\n') % n)
            else:
                conn.write(_('You have no seek %d.\n') % n)
        else:
            if conn.user.session.seeks:
                for s in conn.user.session.seeks:
                    s.remove()
                conn.write(_('Your seeks have been removed.\n'))
            else:
                conn.write(_('You have no active seeks.\n'))

@ics_command('play', 'i')
class Play(Command, MatchMixin):
    def run(self, args, conn):
        if conn.user.session.game:
            if conn.user.session.game.gtype == game.EXAMINED:
                conn.write(_('You are examining a game.\n'))
            else:
                conn.write(_('You are playing a game.\n'))
            return

        if type(args[0]) == str:
            u = user.find.by_prefix_for_user(args[0], conn, online_only=True)
            if u:
                conn.write('TODO: play name\n')
        else:
            if args[0] not in seek.seeks:
                # no such seek
                conn.write(_('That seek is not available.\n'))
                return
            s = seek.seeks[args[0]]
            # check censor and noplay
            if not self._check_opp(conn, s.a):
                return
            # TODO: manual seek
            s.a.write_('%s accepts your seek.' % (conn.user.name,))
            s.accept(conn.user)

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
