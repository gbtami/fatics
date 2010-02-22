from test import *

class CommandTest(Test):
        def test_addplayer(self):
                t = self.connect_as_admin()
                t.write('addplayer testplayer nobody@example.com Foo Bar\n')
                self.expect('Added:', t, 'addplayer')
                t.write('addplayer testplayer nobody@example.com Foo Bar\n')
                self.expect('already registered', t, 'addplayer duplicate player')
                t.write('remplayer testplayer\n')
                t.close()

        def test_announce(self):
                t = self.connect_as_admin()
                t2 = self.connect_as_guest()

                t.write("announce foo bar baz\n")
                self.expect('(1) **ANNOUNCEMENT** from admin: foo bar baz', t)
                self.expect('**ANNOUNCEMENT** from admin: foo bar baz', t2)
                self.close(t)
                self.close(t2)

        def test_asetpass(self):
                self.adduser('testplayer', 'passwd')
                t = self.connect_as_admin()
                t2 = self.connect_as_user('testplayer', 'passwd')
                t.write('asetpass testplayer test\n')
                self.expect("Password of testplayer changed", t)
                self.expect("admin has changed your password", t2)
                self.close(t)
                self.close(t2)

                t2 = self.connect()
                t2.write('testplayer\ntest\n')
                self.expect('fics%', t2)
                self.close(t2)
                self.deluser('testplayer')

class PermissionsTest(Test):
        def test_permissions(self):
                t = self.connect_as_guest()
                t.write('asetpass admin test\n')
                self.expect('asetpass: Command not found', t)
                self.close(t)
        

"""not stable
class AreloadTest(Test):
        def runTest(self):
                self.skip()
                t = self.connect()
                t.write('areload\n')
                self.expect('reloaded online', t, "server reload")
                t.close()
"""

# vim: expandtab tabstop=8 softtabstop=8 shiftwidth=8 smarttab autoindent ft=python
