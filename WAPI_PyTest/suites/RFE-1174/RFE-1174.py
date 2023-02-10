import re
import config
import pytest
import unittest
import logging
import subprocess
import pexpect
import getpass
import sys
from time import sleep

class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_show_tcp_timestamps(self):
        logging.info("show tcp timestamps")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        result = child.expect(['enabled.','disabled.'])
        if (result == 'enabled.'):
            child.expect('enabled.')
            child.expect(pexpect.EOF)
        if (result == 'disabled.'):
            child.expect('disabled.')
            child.expect(pexpect.EOF)

    @pytest.mark.run(order=2)
    def test_02_disable_tcp_timestamps(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps disable')
        child.expect('WARNING:  Disabling the tcp_timestamps would impact system wide TCP performance')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('disabled.')
        assert True

    @pytest.mark.run(order=3)
    def test_03_enable_tcp_timestamps(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps enable')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('enabled.')
        assert True

    @pytest.mark.run(order=4)
    def test_04_show_tcp_timestamps_member(self):
        logging.info("show tcp timestamps")
        print(config.grid_member1_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        result = child.expect(['enabled.','disabled.'])
        if (result == 'enabled.'):
            child.expect('enabled.')
            child.expect(pexpect.EOF)
        if (result == 'disabled.'):
            child.expect('disabled.')
            child.expect(pexpect.EOF)

    @pytest.mark.run(order=5)
    def test_05_disable_tcp_timestamps_member(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps disable')
        child.expect('WARNING:  Disabling the tcp_timestamps would impact system wide TCP performance')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('disabled.')
        assert True

    @pytest.mark.run(order=6)
    def test_06_enable_tcp_timestamps_member(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps enable')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('enabled.')
        assert True

    @pytest.mark.run(order=7)
    def test_07_preserve_tcp_timestamps_enable_after_reboot(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps enable')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('enabled.')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        child.expect('SYSTEM REBOOTING!')
        sleep(200)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('enabled.')
        child.expect('Infoblox >')

    @pytest.mark.run(order=8)
    def test_08_preserve_tcp_timestamps_disable_after_reboot(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        sleep(10)
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set tcp_timestamps disable')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('disabled.')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        child.expect('SYSTEM REBOOTING!')
        sleep(200)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show tcp_timestamps')
        child.expect('disabled.')
        child.expect('Infoblox >')
        assert True

