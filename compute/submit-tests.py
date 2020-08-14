#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import unittest, requests, time, os, json,random, string, yaml, minio,logging
from funcs import *
from datetime import datetime
import kubernetes as k


class TestFindPods(unittest.TestCase):

    def test_pod_there(self):
        self.assertTrue(find_pod('sparkdriver'))

    def test_no_pod_with_that_name(self):
        self.assertFalse(find_pod('randomnamethatisntapod'))


class TestCreateService(unittest.TestCase):

    def test_create_valid_service(self):

        f = open('./yamls/test-service.yaml')
        service_def = yaml.safe_load(f)

        created = create_service(service_def)

        time.sleep(1)
        services = list_services()

        test = 'test-service' in services

        if created:
            delete_service('test-service')

        self.assertTrue(test)

    def test_create_invalid_service(self):

        f = open('./yamls/failed-service.yaml')
        service_def = yaml.safe_load(f)

        created = create_service(service_def)

        time.sleep(1)
        services = list_services()

        test = 'test-service' in services

        if created:
            delete_service('test-service')

        self.assertFalse(test)

class TestCreatePod(unittest.TestCase):

    def test_create_valid_pod(self):

        f = open('./yamls/sample-pod.yaml')
        pod_def = yaml.safe_load(f)

        created = create_pod(pod_def)

        time.sleep(1)
        pods = list_pods()

        test = 'test-pod' in pods

        if created:
            delete_pod('test-pod')

        self.assertTrue(test)

    def test_create_invalid_pod(self):

        f = open('./yamls/sample-broken-pod.yaml')
        pod_def = yaml.safe_load(f)

        created = create_pod(pod_def)

        time.sleep(1)
        pods = list_pods()

        test = 'test-pod' in pods

        if created:
            delete_pod('test-pod')

        self.assertFalse(test)

class TestDeletePod(unittest.TestCase):

    def test_delete_valid_pod(self):

        f = open('./yamls/sample-pod.yaml')
        pod_def = yaml.safe_load(f)

        created = create_pod(pod_def)

        time.sleep(1)
        pods = list_pods()

        test = 'test-pod' in pods

        if test:
            delete = delete_pod('test-pod')

        time.sleep(1)
        pods = list_pods()

        test = 'test-pod' in pods

        self.assertFalse(test)

    def test_delete_invalid_pod(self):

        delete = delete_pod('nonrealpod')

        self.assertFalse(delete)

if __name__ == '__main__':
    unittest.main()
