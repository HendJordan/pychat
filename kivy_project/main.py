import sys
import urllib
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.core.window import Window
#from kivy.garden.mapview import MapView, MapMarker
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.clock import Clock
import json
import ast


from multiselect import *

class WMBA(App):
	"""
	App which acts as the client side of the Where my bros at application
	This app communicates with a flask server over http to communicate changes in entities.
	"""
	def build(self):
		"""
		Initialization of the app. This method builds the authentication form."""
		Window.softinput_mode="below_target"
		self.root = BoxLayout(orientation='vertical')
		self.username = TextInput(text='', hint_text="Username", multiline=False)
		self.password = TextInput(text='', hint_text="Password", multiline=False, password=True)
		self.email = TextInput(text='', hint_text="Email", multiline=False)
		self.noacct = Button(text="Create new account", on_press=lambda x: self.createAccount())
		self.submit = Button(text="Submit", on_press=lambda x: self.auth())
		self.root.add_widget(self.username)
		self.root.add_widget(self.password)
		self.root.add_widget(self.email)
		self.root.add_widget(self.submit)
		self.root.add_widget(self.noacct)
		return self.root

	def auth(self):
		"""Send authentication information to flask server for validation"""
#		print("auth called")
		params = "{\"username\": \"" + self.username.text + "\", \"password\": \""+ self.password.text+ "\"}"
		headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
		req = UrlRequest('http://138.68.21.198:5000/broschat/login', 
			on_success=self.loginsuccess, req_body=params, req_headers=headers)
		req.wait()

	def createAccount(self):
		"""Send the new account data to the server for validation and creation if appropriate."""
#		print("createAccount called")
		params = ("{\"username\": \"" + self.username.text + "\", \"password\": \""
			+ self.password.text+ "\", \"email\": \""+self.email.text+"\"}")
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                req = UrlRequest('http://138.68.21.198:5000/broschat/createuser', 
			on_success=self.loginsuccess, req_body=params, req_headers=headers)
                req.wait()


	def loginsuccess(self, req, result):
		"""The callback of the auth and createaccount methods.
		Based on the json response, success or failure of login is determined.
		Either the user will proceed to the mainDisplay or an error message will be displayed in a popup as appropriate."""
#		print(result)
		if result["success"]:
			self.token = str(result["token"])	
			self.userid = str(result["id"])
			self.mainDisplay()
		else:
			b = Button(text="Close")
			popup = Popup(title=result["error"], content=b, size= (20, 20))
			b.bind(on_press=popup.dismiss)
			popup.open()		
	


	def mainDisplay(self):
		"""Shows list of groups that the user is a member of.
		Displays create new group button so that a user can create
		 a new group if desired.
		Also creates a refresh button so that a user can refresh the list 
		for groups that have been added since the page last loaded."""
		self.root.clear_widgets()
		self.layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, height = 0)
		sv = ScrollView()
		sv.add_widget(self.layout)
		
		self.root.add_widget(sv)
		self.fetchAvailableGroups()
		refreshbttn = Button(text="Refresh groups list", on_press=lambda x: self.fetchAvailableGroups(), size_hint_y=None, height=200)
		createGroup = Button(text="Create new group", on_press=lambda x: self.createGroup(), size_hint_y=None, height=200)
		self.root.add_widget(createGroup)
		self.root.add_widget(refreshbttn)
#		self.getGroupChats()
	
	def fetchAvailableGroups(self):
		"""Makes http request to server to get the list of groups
		 that the user has access to."""
                params = ("{\"userid\": \""+self.userid +"\", \"token\": \""+self.token+"\"}")
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                req = UrlRequest('http://138.68.21.198:5000/broschat/fetchgroups',
                                on_success=self.showgroups, req_body=params, req_headers=headers)
                req.wait()

	def placeholder(self, key):
		return lambda x: self.loadchatview(key)

	def placeholder_2(self, friend, b):
		return lambda x: self.friendSelected(friend, b)

	def showgroups(self, req, result):
		"""Convert json list of groups into a series of button
		 widgets to add to the mainDisplay's scrollview. So that the user can scroll through and click on a particular group."""
		print(result)
		self.layout.clear_widgets()
		groups = ast.literal_eval(result["groups"])
		i=0	
		for key in groups:
			i=i+1
			b = Button(text=groups[key], on_press=self.placeholder(key))
			self.layout.add_widget(b)		
		self.layout.height=200*i
		

	def createGroup(self):
		"""Display's form for creating a new group."""
		self.root.clear_widgets()
		self.gn = TextInput(hint_text="Group name", multiline=False, size_hint_y=None ,height = 200)
#		MultiSelect(text="Select friends for group.")
		#TODO: Build a mutli select dropdown field for users
		self.flist = ""
		self.sv = ScrollView()
		self.layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, height = 0)
		self.layout.add_widget(Label(text="Select users to be members of the new group."))
		self.layout.height = 200
#		self.flistfield = TextInput(hint_text="Comma seperated list of usernames")	
		self.sv.add_widget(self.layout)
		self.fetchFriends() 
#		flist.values = self.flist
				
		b = Button(text="Submit", on_press=lambda x: self.submitGroup(), size_hint_y=None, height=200)
		c = Button(text="Cancel", on_press=lambda x: self.mainDisplay(), size_hint_y=None, height=200)
		self.root.add_widget(self.gn)
		self.root.add_widget(self.sv)
		self.root.add_widget(b)
		self.root.add_widget(c)

	def submitGroup(self):
		"""Callback for submit group button on createGroup view.
		Makes http request to server to create the new group with 
		the list of users included as members."""
#		print("submitting")
		#flist = self.flistfield.text 
#		p = Popup(title="Create new group", content=b)
                params = ("{\"groupname\": \""+self.gn.text+"\", \"friends\": \"" + self.flist + "\", \"userid\": \""+self.userid+"\", \"token\": \""+self.token+"\"}")
 		headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                req = UrlRequest('http://138.68.21.198:5000/broschat/creategroup', 
				on_success=self.newgroupsuccess, req_body=params, req_headers=headers)
                req.wait()

	def newgroupsuccess(self, req, result):
		"""Determines if creating the new group was a success.
		Returns to the mainDisplay regardless."""
		if result["success"]:
			self.mainDisplay()		

	def fetchFriends(self):
		"""Makes http reqest to get list of friends, 
		though at this point friends are not implemented, 
		so it is really just a list of users in the system."""
#		print("Fetching friends")
		params = ("{\"token\": \""+ self.token + "\", \"userid\": \""+self.userid+"\"}" )
		headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
		req = UrlRequest("http://138.68.21.198:5000/broschat/getfriendslist",
				req_body=params, req_headers=headers, on_success=self.fetchFriendsSuccess)
		req.wait()

	def fetchFriendsSuccess(self, req, result):
		"""Takes list of users and adds them to local variable."""
#		print("fetched friends ", result)
		if result["success"]:
			print(result["flist"])
			flistdict = result["flist"]#.split(",")
			print(flistdict)
			i = 0
			for friend in flistdict:
				if friend != self.userid:
					b = Button(text=flistdict[friend], size_hint_y=None, height=100)
					b.bind(on_press=self.placeholder_2(flistdict[friend], b))
					self.layout.add_widget(b)
					i = i+1
			self.layout.height = i*200
		else:
			print(result["error"])

	def friendSelected(self, friend, b):
		self.layout.remove_widget(b)
		self.layout.height-=100
		if len(self.flist) > 0:
			self.flist = self.flist + ","+friend
		else:
			self.flist = friend
		print(self.flist)
		

	def loadchatview(self, gid):
		"""Loads the chat view for a particular group.
		 Sets a interval event to refresh the chat every 5 seconds.
		 Wanted to use sockets for that, but kivy doesn't seem to support them.
		 The messages are displayed inside a dynamically expanding scrollview."""
#		print(gid)
		self.groupid = gid
#		self.num_messages=1
		self.root.clear_widgets()
		self.layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, height = 0)
#, row_default_height= '48dp', row_force_default=True)

#		label = Label(text="Swag dollar")
		self.txt1 = TextInput(text='', hint_text="Enter message here.", multiline=False, size_hint_y=None, height=200)
		self.backbttn = Button(text="Back", on_press=self.goback, size_hint_y=None, height=200)
		self.txt1.bind(on_text_validate=self.submit_message)
		self.sv = ScrollView()
#		self.layout.add_widget(label)
#		m1 = MapMarker(lon = lon, lat = lat)
		self.sv.add_widget(self.layout)
#		view = MapView()
#		view.add_marker(m1)
		self.root.add_widget(self.sv)
		self.root.add_widget(self.txt1)
		self.root.add_widget(self.backbttn)
#		self.root.add_widget(view)
		self.event = Clock.schedule_interval(self.refreshchat, 5)
		self.refreshchat()
		#return root

	def goback(self, arg):
		"""The callback for the back button. 
		 Cancels the interval chat refresh event and returns to the mianview."""
		self.event.cancel()
		self.mainDisplay()

	def submit_message(self, value):
		"""Send message containing group id, sent user id and the value to the server. Message is stored in database so that everyone will see the new message next time their chat refreshes"""
                params = ("{\"groupid\": \""+self.groupid+"\", \"token\": \""+ self.token + "\", \"userid\": \""+self.userid+"\", \"content\": \""+value.text+"\"}" )
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                req = UrlRequest("http://138.68.21.198:5000/broschat/sendmessage",
                                req_body=params, req_headers=headers, on_success=self.refreshchat)
		self.txt1.text = ""
                req.wait()
	
	def refreshchat(self, *args):
		"""Interval callback to refresh the message contents of the chat. Also called after group is first entered by the user. Makes http request containing group id to get messages for."""
		#don't really care about *args because we are just refreshing the chat content
#		print("Refreshing chat")
		params = ("{\"groupid\": \""+self.groupid+"\", \"token\": \""+ self.token + "\", \"userid\": \""+self.userid+"\"}" )
                headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
                req = UrlRequest("http://138.68.21.198:5000/broschat/getallmessages",
                                req_body=params, req_headers=headers, on_success=self.updatechatcontents)
       #         req.wait() dont want to make this synchronous, it's going to get called a lot

	def updatechatcontents(self, req, response):
		"""Use the results of the chat update http request to update the messages displayed to the user. This is a 'dumb' system for now, because all of the messages are updated every time. In the future it would be wise to keep track of messages the user already has and only add new messages to the display instead of removing and reloading the entire list."""
#		print(response)
		if "messages" in response.keys():
			i=0
			self.layout.clear_widgets()
			for m in response["messages"]:
				l = Label(text=m["message"]+" - "+m["sent_username"], size_hint_y=None)
				l.bind(texture_size = lambda instance, value: setattr(instance, 'height', value[1]))
				l.bind(width=lambda instance, value: setattr(instance, "text_size", (value, None)))
#				l.height=l.texture_size[1]
#				l.text_size = text_size=(Window.width - Window.width/5, None)
#				l.bind(size=label_size(l, (Window.width/2, Window.height/15)))
				i=i+1
				self.layout.add_widget(l)
			self.layout.height = i*200
#			self.sv.scroll_to(l, animate=True)
#
#def label_size(obj, size):
#	obj.size = size

	def on_pause(self):
		"""Handles behavior for when user switches to a different application to focus without exiting this app completely."""
		return True
	
	def on_resume(self):
		"""Handles re-focus after previous pause."""
		pass
				
		
if __name__ == '__main__':
	WMBA().run()
