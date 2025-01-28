import unittest
from unittest.mock import patch, MagicMock
import datetime
import pytz
import sys
import os

# Dynamically add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.vuegraf import vuegraf

class TestVuegraf(unittest.TestCase):

    @patch('vuegraf.datetime')
    def test_log(self, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime(2025, 1, 12, 0, 0, 0, tzinfo=datetime.timezone.utc)
        with patch('builtins.print') as mock_print:
            vuegraf.log('INFO', 'Test message')
            mock_print.assert_called_with('2025-01-12 00:00:00+00:00 | INFO  | Test message', flush=True)

    def test_getConfigValue(self):
        vuegraf.config = {'test_key': 'test_value'}
        self.assertEqual(vuegraf.getConfigValue('test_key', 'default_value'), 'test_value')
        self.assertEqual(vuegraf.getConfigValue('nonexistent_key', 'default_value'), 'default_value')

    @patch('vuegraf.PyEmVue')
    def test_populateDevices(self, MockPyEmVue):
        mock_vue = MockPyEmVue.return_value
        mock_vue.get_devices.return_value = []
        account = {'vue': mock_vue}
        vuegraf.populateDevices(account)
        self.assertIn('deviceIdMap', account)
        self.assertIn('channelIdMap', account)

    @patch('vuegraf.PyEmVue')
    def test_lookupDeviceName(self, MockPyEmVue):
        mock_vue = MockPyEmVue.return_value
        mock_vue.get_devices.return_value = []
        account = {'vue': mock_vue, 'deviceIdMap': {}}
        self.assertEqual(vuegraf.lookupDeviceName(account, '12345'), '12345')

    @patch('vuegraf.PyEmVue')
    def test_lookupChannelName(self, MockPyEmVue):
        mock_vue = MockPyEmVue.return_value
        mock_vue.get_devices.return_value = []
        account = {'vue': mock_vue, 'deviceIdMap': {}}
        chan = MagicMock()
        chan.device_gid = '12345'
        chan.channel_num = '1'
        self.assertEqual(vuegraf.lookupChannelName(account, chan), '12345-1')

    @patch('vuegraf.influxdb_client.Point')
    def test_createDataPoint(self, MockPoint):
        point = vuegraf.createDataPoint('account', 'device', 'channel', 100, '2025-01-12T00:00:00Z', 'detailed')
        self.assertIsNotNone(point)

    @patch('vuegraf.query_api.query')
    def test_getLastDBTimeStamp(self, mock_query):
        mock_query.return_value = []
        start_time, stop_time, history_flag = vuegraf.getLastDBTimeStamp('channel', 'minute', datetime.datetime.now(), datetime.datetime.now(), False)
        self.assertFalse(history_flag)

if __name__ == '__main__':
    unittest.main()
