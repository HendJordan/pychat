# pychat


The pychat applicatin consists of two seperate code bases.
1) main.py is the kivy application which can be packaged into an apk for mobile install via
   the command buildozer android debug deploy run. This will use the local buildozer.spec file 
   to compile an apk in the local bin directory. This apk can be sent to and installed on any
   android device which allows install of unsigned applications (usually just a setting in
   the device.

2) The other piece is the server side code. The code for the application itself is inside the 
   pychat directory, with the app defined in __init__.py, the other files database.py and 
   models.py are support files which contain database connection initialization and entity 
   models respectively. 
   In the top level directory is the runserver.py file which imports pychat and starts the 
   server instance. This is the traditional way of packaging larger flask applications.
   For the mobile app to work, this flask server instance must be running.

To run the appliction build the apk on a linux machine 
(with buildozer, python-for-android and kivy installed) using the 
command "buildozer android debug deploy run". If an android device is connected to the
machine the application should automatically load and run on the device 
(as long as USB debugging is enabled). A .apk file can also be found in the bin folder in the 
local directory (this folder will be created if it does not yet exist). 
This apk can be installed on any android device which allows for instillation of unsigned 
applications.

Once the apk file is installed and the flask server is running, launch the application on the 
android device. The user should see a simple layout of three text inputs and two buttons.
Initially the user will not have an account, so create one by filling out the username, password
and email fields before pressing the create new account button. If the username or email values
are not unique, the account will not be created and an error message displayed.
Once you have created an account the next time you log into the system simply fill out the 
username and password fields, the email field is only required when creating an account.

Once the user has created an account or logged in, they will be presented with a blank (for now)
page apart from two buttons, create group and refresh group list. Once the user is a member of
one or more groups, the groups will appear in a scrollable list on this page. At this point the 
user can create a group by clicking the create group button, which will bring them to the 
group creation page. The text field at the top is for entering the optional group name. 
Below that is a list of other users in the system. To add a user to the group simply tap the
button with their name on it. The process can be canceled by pressing the cancel button, which
will return the user to the page with the list of groups.
Once the user is satisfied with the group configuration they can tap the submit button to create
the group. Submission of the group returns the user to the page with the list of groups.
The user should now see their newly created group in the list. Any users who are also members 
of this group will see the group in their list as well. Depending on when the page was loaded 
last, it may be necessary for the user to refresh their list of groups by pressing the refresh button at the bottom of the page before the new group will appear.
At this point the user may tap any of the buttons with group names on them, this will take them
to the chat view for that particular group.

Once in the chat view the user will see a scrollable list of messages (initially empty).
Any member of the chat can create a new message by typing in the text field at the bottom of 
the screen. Press enter to submit the message. After a breif delay the message will be visible 
in the chat to all members of the group. This includes those who are activly viewing the chat.
The chat will automatically refresh and update with the newest content. Each message will 
display the content of the message entered by the user along with the username of whoever
sent it at the end. The user may go back to the list of groups by pressing the back button at 
any time.


The backend must be ran on a properly configured linux server with flask and sqlalchemy 
installed. An instance of a flask server will launch if you use the command python runserver.py
from the application directory. By default this is launched on localhost at port 5000, 
if that is not desireable the user can adjust it by changing the host and port parameters in 
the runserver.py file. The user will need to modify the database file in the pychat directory.
This file needs to contain valid mysql username and password credentials in the create engine 
statement, if this is not updated the application will not work. All traffic from the 
application is http so keep that under consideration while setting passwords and relaying 
sensitive information. Messages are stored in the dabase as plain text, passwords are stored 
encrypted using the werkzeug module to hash the password, however passwords are vulnerable to 
interception during initial create user and login requests via any http monitoring tool.

NOTE:
Included in the server side code archive is a directory called scripts. This directory contains
a series of install and upgrade mysql scripts used during development. The latest install 
script may be used to create the broschat database. Also included in this directory is a 
database dump of the database with test data in its current state. This may be used to create
the pychat database pre-populated with some test data. The command line operation for 
bulding a databse from a mysql dump file is "mysqldump -u username -p databasename < databasedump.sql"


