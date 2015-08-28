#!/usr/bin/python

import argparse, re, signal, subprocess, sys, time
import dot3k.lcd as lcd
import dot3k.backlight as backlight

killed = False
ip_addr = ''

backlight.rgb(255, 105, 50)


def get_interfaces():
        parser = argparse.ArgumentParser(description='Show IP address \
                of connected network interfaces')
        parser.add_argument('interfaces', type=str, nargs='*',
                            help='Network interfaces to display')

        args = parser.parse_args()
        if not args.interfaces:
                return ['wlan0', 'eth0']

        return args.interfaces


def signal_handler(signal, frame):
        lcd.clear()
        backlight.off()
        sys.exit(0)

def check_output(device):
        ifconfig = subprocess.check_output(['ifconfig', device])
        return ifconfig


def check_up(device):
        path = '/sys/class/net/'+device+'/operstate'
        device_up = (subprocess.check_output(['cat', path]) == 'up\n')
        return device_up


# on kill, call signal_handler
signal.signal(signal.SIGTERM, signal_handler)

while(not killed):
        pattern = re.compile('(inet\ addr:)(\d+.\d+.\d+.\d+)')

        devices = get_interfaces()

        for device in devices:
            try:

                ifconfig = check_output(device)

                device_up = check_up(device)

                if (device_up):
                        ip_info = pattern.search(ifconfig)

                        while(ip_info is None):
                                lcd.write('Disconnected')
                                ifconfig = check_output(device)
                                ip_info = pattern.search(ifconfig)

                        new_ip = ip_info.group(2)

                        if (new_ip != ip_addr):
                                lcd.clear()
                                lcd.write(device)
                                lcd.set_cursor_position(0, 1)
                                lcd.write(new_ip)
                                ip_addr = new_ip

                else:
                        lcd.clear()
                        lcd.write(device)
                        lcd.set_cursor_position(0, 1)
                        lcd.write('Disconnected')
                        ip_addr = ''

            except subprocess.CalledProcessError as e:
                    #  a device could be disconnected during loop
                    #  execution, if so, just continue to the
                    #  next device
                    lcd.clear()
                    lcd.write(device)
                    lcd.set_cursor_position(0, 1)
                    lcd.write('Device not found')
                    ip_addr = ''
            time.sleep(5)
