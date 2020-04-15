import unittest
from funcs import *
import requests
import time
import os
import json
from datetime import datetime
import random
import string
import yaml
import kubernetes as k
import minio

class TestFindPods(unittest.TestCase):

    def test_pod_there(self):
        self.assertTrue(find_pod('sparkdriver'))

    def test_no_pod_with_that_name(self):
        self.assertFalse(find_pod('randomnamethatisntapod'))

class Test_pod_running(unittest.TestCase):

    def test_running_pod(self):
        self.assertTrue(pod_running('sparkdriver'))

    def test_non_real_pod(self):
        self.assertFalse(pod_running('randomnamethatisntapod'))

    def test_completed_pod(self):
        self.assertFalse(pod_running('submit-pi-test-1582213087041-driver'))

class Test_get_pod_logs(unittest.TestCase):

    def test_status_succeded_pod(self):

        status, logs = get_pod_logs('submit-pi-test-1582213087041-driver')

        self.assertEqual(status,'Succeeded')

    def test_status_running_pod(self):

        status, logs = get_pod_logs('sparkdriver')

        self.assertEqual(status,'Running')


if __name__ == '__main__':
    unittest.main()
