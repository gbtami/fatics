import trie
import channel
import admin
import user
from db import *

lists = trie.Trie()

class MyList(object):
        #[perm_head, perm_god, perm_admin, perm_public, perm_personal] = range(5)
        def __init__(self, name):
                self.name = name
                lists[name.lower()] = self

class ListError(Exception):
        def __init__(self, reason):
                self.reason = reason

class TitleList(MyList):
        def __init__(self, id, name, descr):
                MyList.__init__(self, name)
                self.id = id
                self.descr = descr

        def add(self, args, conn):
                if conn.user.admin_level < admin.level.admin:
                        raise ListError(_("You don't have permission to do that."))
                u = user.find.by_name_or_prefix_for_user(args[1], conn)
                if u:
                        if u.is_guest:
                                raise ListError(_("You cannot give a guest a title."))
                        try:
                                db.user_add_title(u.id, self.id)
                        except DuplicateKeyError:
                                raise ListError(_('%s is already in the %s list.') % (u.name, self.name))
                        else:
                                if u.is_online:
                                        u.make_title_str()
                                conn.write(_('%s added to the %s list.\n') % (u.name, self.name))

        def show(self, args, conn):
                conn.write('%s: ' % self.name.upper())
                for user_name in db.title_get_users(self.id):
                        conn.write('%s ' % user_name)
                conn.write('\n')

        def sub(self, args, conn):
                if conn.user.admin_level < admin.level.admin:
                        raise ListError(_("You don't have permission to do that."))
                u = user.find.by_name_or_prefix_for_user(args[1], conn)
                if u:
                        assert(not u.is_guest)
                        try:
                                db.user_del_title(u.id, self.id)
                        except DeleteError:
                                raise ListError(_("%s is not in the %s list.") % (u.name, self.name))
                        else:
                                if u.is_online:
                                        u.make_title_str()
                                conn.write(_('%s removed from the %s list.\n') % (u.name, self.name))

class ChannelList(MyList):
        def add(self, args, conn):
                try:
                        val = int(args[1], 10)
                        channel.chlist[val].add(conn.user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))


        def sub(self, args, conn):
                try:
                        val = int(args[1], 10)
                        channel.chlist[val].remove(conn.user)
                except ValueError:
                        raise ListError(_('The channel must be a number.'))
                except KeyError:
                        raise ListError(_('Invalid channel number.'))

"""a list of lists"""
class ListList(object):
        def __init__(self):
                ChannelList("channel")
               
                for title in db.title_get_all():
                        TitleList(title['title_id'], title['title_name'], title['title_descr'])
        
ListList()

#  removedcom filter muzzle, cmuzzle, c1muzzle, c24muzzle, c46muzzle, c49muzzle, c50muzzle, c51muzzle,
# censor, gnotify, noplay, channel, follow, remote, idlenotify


# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent
