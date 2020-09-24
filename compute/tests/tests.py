#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import unittest, sys, os,json
sys.path.append(".")
from funcs import *
from jobClass import *
import compute_class
import flask

class test_app_auth(unittest.TestCase):

    def setUp(self):
        compute_class.app.config['TESTING'] = False
        self.app = compute_class.app.test_client()

    def test_missing_auth(self):

        data = {'dataset_ids':['test'],'software_ids':'test2'}
        req = self.app.post('/job',data = json.dumps(data),content_type='multipart/form-data')

        self.assertEqual(req.status_code,403)

class test_app_no_auth(unittest.TestCase):

    def setUp(self):
        compute_class.app.config['TESTING'] = True
        self.app = compute_class.app.test_client()

    def test_no_auth(self):

        data = {'dataset_ids':['test'],'software_ids':'test2'}
        req = self.app.post('/job',data = json.dumps(data),content_type='multipart/form-data')

        self.assertEqual(req.status_code,400)


if __name__ == '__main__':
    unittest.main()
