#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import unittest, sys, os
sys.path.append(".")
from funcs import *
import requests


# class TestFindPods(unittest.TestCase):
#
#     def test_pod_there(self):
#         self.assertTrue(find_pod('sparkdriver'))
#
#     def test_no_pod_with_that_name(self):
#         self.assertFalse(find_pod('randomnamethatisntapod'))
#
# class Test_pod_running(unittest.TestCase):
#
#     def test_running_pod(self):
#         self.assertTrue(pod_running('sparkdriver'))
#
#     def test_non_real_pod(self):
#         self.assertFalse(pod_running('randomnamethatisntapod'))
#
#     def test_completed_pod(self):
#         self.assertFalse(pod_running('submit-pi-test-1582213087041-driver'))
#
# class Test_get_pod_logs(unittest.TestCase):
#
#     def test_status_succeded_pod(self):
#
#         status, logs = get_pod_logs('submit-pi-test-1582213087041-driver')
#
#         self.assertEqual(status,'Succeeded')
#
#     def test_status_running_pod(self):
#
#         status, logs = get_pod_logs('sparkdriver')
#
#         self.assertEqual(status,'Running')
#
# class Test_gather_outputs(unittest.TestCase):
#
#     def test_empty_folder(self):
#
#          outputs = gather_job_outputs('randomtestofemptyfolder')
#
#          self.assertEqual(outputs,[])
#
#     def test_non_empty(self):
#
#         outputs = gather_job_outputs('EEG')
#
#         expected = ['EEG/OperationsFile.py','EEG/Periphery.py','EEG/eeg_500_OG.csv','EEG/runOG.py']
#
#         self.assertEqual(outputs,expected)






if __name__ == '__main__':
    unittest.main()
