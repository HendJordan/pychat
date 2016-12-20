import sys
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
import json
from database import db_session, init_db
from models import User, Friend, Group, Message, GroupMember

init_db()

app = Flask(__name__)

@app.route("/pychat")
def hello():
	return "Ahoy!"

@app.route("/pychat/login", methods=["POST"])
def login():
	"""Login api, checks username and password against database. Returns result of whether they match, if they match successfully the client is provided a token to user for user verification in other api calls."""
#	print(request.data)
#	content = request.form.keys()[0]
	try:
		content = json.loads(request.data)
		username=content["username"]
		password = content["password"]
		u = db_session.query(User).filter(User.username == username).first()
		if u and  check_password_hash(u.password, password):
			return jsonify({"success": 1, "token": u.password, "id": u.id})
	except ValueError:
		print("ValueError in data")
	
#	print(content["username"], content["password"])
	return jsonify({"success": 0, "token": None, "id": None, "error": "Incorrect username or password."})

@app.route("/pychat/creategroup", methods=["POST"])
def creategroup():
	"""Api for creating a new group. Parameters are stored and the call returns success along with the new group's id if appropriate."""
	try:
		content = json.loads(request.data)
#		print(content)
		unames = content["friends"].split(",")
#		print(unames)
		groupname = content["groupname"]
#		print(groupname)
		userid = int(content["userid"])
#		print(userid)
		token = content["token"]
#		print(token)
		if validate_user(userid, token):
#			print(unames)
			g = Group(userid, groupname)
			db_session.add(g)
			db_session.commit()
			for uname in unames:
#				print(uname)
				res = db_session.query(User).filter(User.username==uname)
				if res.count() == 1:
					u = res.first()
					gm = GroupMember(u.id, g.id)
					db_session.add(gm)
			#add one for current user
			gm = GroupMember(userid, g.id)
			db_session.add(gm)

			db_session.commit()
			return jsonify({"success": 1, "groupid": g.id, "error": None})
		else:
			return jsonify({"success": 0, "groupid": None, "error": "User did not validate"})
	except:
		print(sys.exc_info()[0])
		return jsonify({"success": 0, "groupid": None, "error": "An unexpected error has occurred"})
	
@app.route("/pychat/createuser", methods=["POST"])
def createuser():
	"""API for creating a new user, password is hashed before being stored in the database. Check's to make sure username and email are unique, returns success and a token if appropriate."""
	try:
		content = json.loads(request.data)
		p = generate_password_hash(content["password"])
		un  = content["username"]
		e = content["email"]
#		print(un)
#		print(e)
##		print(p)
		if unique(User.username, un) and unique(User.email, e):
			u = User(str(un), str(e), str(p))
			db_session.add(u)
			db_session.commit()
			return jsonify({"success": 1, "token": p, "id": u.id})
		else:
			return jsonify({"success": 0, "token": None, "error": "Username or email already in use."})
	except:
#		print(sys.exc_info()[0])
		return jsonify({"success": 0, "token": None, "error": "An unexpected error occurred."})

@app.route("/pychat/getfriendslist", methods=["POST"])
def getfriendslist():
	"""A little missleading, this api returns a list of all users in the system as friends are not yet implemented."""
#	print("getting friends list")
	userlist = db_session.query(User)
	flist = {}
	for obj in userlist:
#		print(obj.id, obj.username)
		flist[obj.id] = obj.username
	return jsonify({"success": 1, "flist": flist, "error": None })

@app.route("/pychat/fetchgroups", methods=["POST"])
def fetchgroups():
	"""Api returns a list of groups that the user is a member of."""
	try:
		content = json.loads(request.data)
		userid = content["userid"]
		token = content["token"]
		groups = {}
		if validate_user(userid, token):
#			print(userid)
			res = db_session.query(GroupMember).filter(GroupMember.user_id == userid)
#			print(res.count())
			for gid in res:
#				print(gid.id)
				g = db_session.query(Group).filter(Group.id == gid.groupid)
#				print(g.count())
				if g.count() > 0:
#					print("found one")
#					print(g.first().id)
					groups[g.first().id] = g.first().name
			return jsonify({"success": 1, "groups": json.dumps(groups)})
		else:
			return jsonify({"success": 0, "groups": None, "error": "User did not validate"})
	except:
 #               print(sys.exc_info()[0])
                return jsonify({"success": 0, "groups": None, "error": "An unexpected error occurred."})

@app.route("/pychat/sendmessage", methods=["POST"])
def sendmessage():
	"""Api for storing a new message. message text and metadata are stored in the database with a group id and sent_userid to indicate which group the message belongs to and which member sent it."""
	try:
		content = json.loads(request.data)
		userid = content["userid"]
		groupid = content["groupid"]
		message = content["content"]
		token = content["token"]
		if validate_user(userid, token):
			m = Message(groupid, userid, message)
			db_session.add(m)
			db_session.commit()
#			print("Committed message: "+ message)
			return jsonify({"success": 1})
		else:
			return jsonify({"success": 0})
	except:
#		print(sys.exc_info()[0])
                return jsonify({"success": 0, "error": "An unexpected error occurred."})

@app.route("/pychat/getallmessages", methods=["POST"])
def getmessages():
	"""Api returns list of all messages for a particular group."""
	try:
		content = json.loads(request.data)
		groupid = content["groupid"]
		userid = content["userid"]
		token = content["token"]
		data = []
#		print("Fetching messages for group: "+groupid)	
		if validate_user(userid, token):
			res = db_session.query(Message).filter(Message.groupid==groupid)
#			print(res.count())
			for obj in res:
#				print(obj)
				name = db_session.query(User).filter(User.id==obj.sent_userid).first().username
				record = {
					"message": obj.content, 
					"sent_username": name
					}
				data.append(record)
			return jsonify({"messages": data})
		else:
			return jsonify({"success": 0})

	except:
               print(sys.exc_info()[0])
               return jsonify({"success": 0, "error": "An unexpected error occurred."})



@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()

#def getMessages(groupid):
	

def unique(obj, val):
	"""Utility function to make sure that a value of a particular field is not currently in the database before we try to save it."""
	if db_session.query(obj).filter(obj==val).count() > 0:
		return False
	return True

def validate_user(userid, token):
	"""Validates a user's identity based on userid and supplied token."""
	u = db_session.query(User).filter(User.id==userid).first()
	return u.password == token

if __name__ == "__main__":
	if 1:
		app.run(host="0.0.0.0", debug=True)
	else:
	        app.run(host="0.0.0.0", port=int(80), debug=True)

