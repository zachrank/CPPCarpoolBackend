import os
import server # import the cpp carpool backend flask app
import unittest

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        #server.app.config['TESTING'] = True
        self.app = server.app.test_client()
        with server.app.app_context():
            #server.init_db()
            pass

    def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(server.app.config['DATABASE'])
        pass

    #note: unittest will run all methods prefixed with 'test_'
    def test_auth(self):
        rv = self.login('testuser', 'testpass')
        assert rv.status_code == 200
        rv = self.login('', '')
        assert rv.status_code == 401
        
    #used for homework #6, delete later
    def test_fuwu(self):
        assert self.app.post('/fuwu', follow_redirects=True).status_code == 75
    #used for homework #6, delete later --carter
    def test_numpy(self):
        assert self.app.post('/nump', follow_redirects=True).status_code == 75

    def login(self, u, p):
        payload = {
            'user': u,
            'password': p
        }
        return self.app.post('/login', data=payload, follow_redirects=True)

if __name__ == '__main__':
    unittest.main()
