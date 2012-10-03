import dbus
import os, sys
import gobject
import pygame


class DeviceAddedListener:

	#constructor
	def __init__(self):
		#set-up interrupt on USB device being plugged (call self._filter)
		self.bus = dbus.SystemBus()
		self.hal_manager_obj = self.bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
		self.hal_manager = dbus.Interface(self.hal_manager_obj, "org.freedesktop.Hal.Manager")
		self.hal_manager.connect_to_signal("DeviceAdded", self.usbInterrupt)
		
		#check for devices that are already plugged in
		self.ud_manager_obj = self.bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
		self.ud_manager = dbus.Interface(self.ud_manager_obj, 'org.freedesktop.UDisks')
		
		for dev in self.ud_manager.EnumerateDevices():
			self.usbPlugged(dev)

	#interrupt when USB device is called
	def usbInterrupt(self, udi):
		device_obj = self.bus.get_object("org.freedesktop.Hal", udi)
		device = dbus.Interface(device_obj, "org.freedesktop.Hal.Device")

		if device.QueryCapability("volume"):
			import time
			while not device.GetProperty("volume.is_mounted"):
				time.sleep(1)
			mount_point = device.GetProperty("volume.mount_point")
			self.scanMp3(mount_point)


	#scan mounted devices	
	def usbPlugged(self, udi):
		device_obj = self.bus.get_object("org.freedesktop.UDisks", udi)
		device = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
		
		if device.Get('org.freedesktop.UDisks.Device', "DeviceIsMounted"):
			paths = device.Get('org.freedesktop.UDisks.Device', "DeviceMountPaths")
			
			for dev in paths:
				if dev != "/":
					self.scanMp3(dev)

	#scan the volume for MP3s and populate data
	def scanMp3(self, path):
		from random import randint
		self.L = []
        
		for file in os.listdir(path + "/"):
			if file[-4:] == ".mp3":
				self.L.append(file)

		song = self.L[ randint(0, len(self.L)) ]
		print "Playing: " + song
		song = path + "/" + song
		pygame.init()
		pygame.mixer.init()
		pygame.mixer.music.load(song)
		pygame.mixer.music.play()


if __name__ == '__main__':
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)
	loop = gobject.MainLoop()
	DeviceAddedListener()
	loop.run()
