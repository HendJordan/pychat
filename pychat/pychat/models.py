from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
	__tablename__='users'
	id = Column(Integer, primary_key=True)
	username = Column(String(50), unique=True)
	password = Column(String(300))
	email = Column(String(100), unique=True)

	def __init__(self, name=None, email=None, password=None):
		self.username = name
		self.email = email
		self.password = password

class Friend(Base):
        __tablename__='friends'
        id = Column(Integer, primary_key=True)
        u1 = Column(Integer)
        u2 = Column(Integer)

        def __init__(self, u1=None, u2=None):
                self.u1 = u1
		self.u2 = u2

class Group(Base):
        __tablename__='groups'
        id = Column(Integer, primary_key=True)
	name = Column(String(100))
        owner = Column(Integer)

        def __init__(self, owner=None, name=None):
                self.owner = owner
		self.name = name

class Message(Base):
        __tablename__='messages'
        id = Column(Integer, primary_key=True)
        groupid = Column(Integer)
        sent_userid = Column(Integer)
	content = Column(String(1000))

	def __init__(self, groupid=None, sent_userid=None, content=None):
                self.groupid = groupid
                self.sent_userid = sent_userid
		self.content = content

class GroupMember(Base):
	__tablename__="group_members_list"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	groupid = Column(Integer)

	def __init__(self, user_id=None, groupid=None ):
		self.user_id = user_id
		self.groupid = groupid




