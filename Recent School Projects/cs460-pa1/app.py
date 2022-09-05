######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cs460'
app.config['MYSQL_DATABASE_DB'] = 'photoshare2'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
        cursor = conn.cursor()
        cursor.execute("SELECT email from Users")
        return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
        users = getUserList()
        email = request.form.get('email')
        if not(email) or email not in str(users):
        	return
        user = User()
        user.id = email
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        user.is_authenticated = request.form['password'] == pwd
        return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
        return render_template('register.html', supress=True, supress_2 = True)


@app.route("/register", methods=['POST'])
def register_user():
	try:
		#optional fields (hometown and gender) not checked
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		dob = request.form.get('dob')
		email = request.form.get('email_2')
		password = request.form.get('password')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test_email = isEmailUnique(email)
	if not test_email:
                return render_template('register.html', supress = False, supress_2 = True)
	test_exist = firstname != '' and lastname != '' and dob != '' and email != '' and password != ''
	if test_email and test_exist:
		fields = " (first_name, last_name, email, birth_date, hometown, gender, password)"
		print(cursor.execute("INSERT INTO Users" +  fields + "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(firstname, lastname, email, dob, hometown, gender, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
                
                print("invalid fields")
                return render_template('register.html', supress=True, supress_2 = False)
               
                #return flask.redirect(flask.url_for('register'))

def getUsersAlbumNamesHelper(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getUsersAlbumNames(uid):
	albumList = getUsersAlbumNamesHelper(uid)
	namesList = []
	for album in albumList:
		namesList.append(album[0])
	return namesList

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getAlbumPhotos(aid):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos WHERE albums_id = '{0}'".format(aid))
	return cursor.fetchall()

def getAlbumTaggedPhotos(aid, tag):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos NATURAL JOIN Tags WHERE albums_id = '{0}' AND tname = '{1}'".format(aid, tag))
	return cursor.fetchall()

def getAlbumTaggedPhotosDefault(aid, tag):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption, first_name, last_name FROM Photos NATURAL JOIN Tags NATURAL JOIN Users WHERE albums_id = '{0}' AND tname = '{1}'".format(aid, tag))
	return cursor.fetchall()


def getUserTaggedPhotos(uid, tag):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption FROM Photos NATURAL JOIN Tags WHERE tname = '{0}' AND user_id = '{1}'".format(tag, uid))
	return cursor.fetchall()

def getAllTaggedPhotos(tag):
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption, first_name, last_name FROM Photos NATURAL JOIN Tags NATURAL JOIN Users WHERE tname = '{0}'".format(tag))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

#end login code

def getAlbumIdFromUidName(uid, name):
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id FROM Albums WHERE user_id = '{0}' AND name = '{1}'".format(uid, name))
	return cursor.fetchall()

def getTagsListFromString(tagstr):
	tagsList = tagstr.split(",")
	return tagsList

def getPhotoId(caption, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Photos WHERE caption = '{0}' AND user_id = '{1}'".format(caption, uid))
	return cursor.fetchone()

def getPhotosDefault():
	cursor = conn.cursor()
	cursor.execute("SELECT data, photo_id, caption, first_name, last_name FROM Photos NATURAL JOIN Users ORDER BY RAND() LIMIT 20")
	return cursor.fetchall()

def getRecPhotos(uid):
        master_list = []
        for i in range(5,0,-1):
                cursor = conn.cursor()
                cursor.execute("SELECT P.data, P.photo_id, P.caption FROM Photos P, (SELECT photo_id, count_val FROM (SELECT photo_id, count(tname) as count_val FROM Tags T_3,(SELECT T_2.tname as tname_2, T_2.photo_id as photo_id_2 FROM Tags T_2,(SELECT tname FROM Tags T join (SELECT P.photo_id from Photos P WHERE P.user_id = '{0}') as user_photos WHERE user_photos.photo_id = T.photo_id GROUP BY tname ORDER BY COUNT(T.photo_id) DESC LIMIT 5) as place WHERE place.tname = T_2.tname) as place_2 WHERE T_3.photo_id = place_2.photo_id_2 GROUP BY(photo_id) HAVING COUNT(DISTINCT tname_2) = '{1}' ORDER BY COUNT(tname) ASC) as first_set WHERE first_set.photo_id not in (SELECT P.photo_id from Photos P WHERE P.user_id = '{0}')) as queried WHERE queried.photo_id = P.photo_id ORDER BY count_val ASC".format(uid, i))
                add = cursor.fetchall()
                if add != ():
                        master_list.append(add[0])
                        
        #print(master_list)
        
        return master_list

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id, name, first_name, last_name FROM Albums NATURAL JOIN Users")
	return cursor.fetchall()

def getAlbumsByUsers():
	all = getAllAlbums()
	albumsByUsers = []
	for i in all:
		albumsByUsers.append((i[1] + " by: " + i[2] + " " + i[3], i[0]))
	return albumsByUsers

def removePhotoDupe(photos):
	noDupe = []
	for photo in photos:
		duped = False
		for dupe in noDupe:
			print("in photo:")
			print(photo[1])
			print("in dupe:")
			print(dupe[1])
			if(photo[1] == dupe[1]):
				duped = True
		if(not duped):
			noDupe.append(photo)
	return noDupe


@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albumList = getUsersAlbumNames(uid)


	if request.method == 'POST':


		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tags = getTagsListFromString(request.form.get('tags'))


		#Create a new album if necessary
		if (request.form.get('album')=="new"):
			albumName = request.form.get('albumname')
			albumDate = request.form.get('albumdate')
			cursor = conn.cursor()
			cursor.execute('''INSERT INTO Albums (name, date, user_id) VALUES (%s, %s, %s)''', (albumName,albumDate,uid))
			conn.commit()
		else:
			albumName = request.form.get('album')

		#Add photo to Photos table
		albumId = getAlbumIdFromUidName(uid, albumName)[0]
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Photos (data, user_id, caption, albums_id) VALUES (%s, %s, %s, %s )''', (photo_data, uid, caption,albumId))
		conn.commit()
		
		#Add tags entry
		photoId = getPhotoId(caption, uid)
		for tag in tags:
			cursor.execute('''INSERT INTO Tags (tname, photo_id) VALUES (%s, %s )''', (tag,photoId))
			conn.commit()


		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), albumList = albumList, base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html', albumList = albumList)
#end photo uploading code

def getUserFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT friend_2 FROM Friends WHERE friend_1 = '{0}'".format(uid))
	return cursor.fetchall()

def getNameFromId(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAlbumIdFromAllList(str):
	num = str.split(",")[1]
	aid = ""
	for c in num:
		if c.isdigit():
			aid = aid + c
	return aid

def getLikes(pid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id, count(*) as user_id FROM Likes WHERE photo_id='{0}'".format(pid))
	return cursor.fetchall()[0][1]

def getReccomendedFriends(uid):
        cursor = conn.cursor()
        cursor.execute("SELECT f_2.friend_2, count(*) from (SELECT friend_2 FROM Friends WHERE friend_1 = '{0}') as f, friends as f_2 WHERE f_2.friend_1 = f.friend_2 AND f_2.friend_2 NOT IN(SELECT friend_2 FROM Friends WHERE friend_1 = '{0}') AND f_2.friend_2 <> '{0}' GROUP BY f_2.friend_2 ORDER BY COUNT(*) DESC".format(uid))
        return cursor.fetchall()

@app.route("/friends", methods=['GET'])
@flask_login.login_required
def friends():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        friendIdList = getUserFriends(uid)
        friendNameList = []

        for i in friendIdList:
                fullName = (getNameFromId(i[0]))
                friendNameList.append(fullName[0][0] + " " + fullName[0][1])

        return render_template('friends.html', friendlist=friendNameList)


def getUsers():
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, email FROM Users")
	textlist = []
	for name in cursor.fetchall():
		fullname = name[0] + " " + name[1] + " " + name[2]
		textlist.append(fullname)
	return textlist

def getEmailfromGetUsers(input):
	return input.rsplit(' ', 1)[1]

def checkExistingFriend(uid1, uid2):
	cursor = conn.cursor()
	if cursor.execute("SELECT 'friend_1' FROM Friends WHERE 'friend_1' = '{0}' AND 'friend_2' = '{1}'".format(uid1,uid2)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
def getTopUsers():
        cursor = conn.cursor()
        cursor.execute("SELECT P_val.user_id, P_val.P_score + C_val.C_score as con_score FROM (SELECT user_id, COUNT(photo_id) as P_score FROM Users U LEFT JOIN Photos P USING(user_id) GROUP BY user_id) as P_val, (SELECT user_id, COUNT(comment_id) as C_score FROM Users U LEFT JOIN Comments C USING(user_id) GROUP BY user_id) as C_val WHERE C_val.user_id = P_val.user_id ORDER by con_score DESC LIMIT 10;")
        return cursor.fetchall()

def getUserList_coms(comment):
		cursor = conn.cursor()
		cursor.execute("SELECT C.user_id,COUNT(*) AS ccount FROM Comments C WHERE C.text='{0}' GROUP BY C.user_id ORDER BY ccount DESC".format(comment))
		interim = cursor.fetchall()
		print(interim)
		return interim

@app.route("/commentsearch", methods = ['GET','POST'])
@flask_login.login_required
def comment_search_post():
		if request.method == 'POST':
				try:	 
						comments = request.form.get('comsearch')
						listOfUsers = getUserList_coms(comments)
						userListVal = []
						print(listOfUsers)
						if listOfUsers != ():
								for i in listOfUsers:
										topName = (getNameFromId(i[0]))
										print(topName)
										userListVal.append([topName[0][0] + " " + topName[0][1]])
								return render_template('commentsearch.html', userList = userListVal)
				except:
						return render_template('commentsearch.html')
					
					

		else:
			return render_template('commentsearch.html')


@app.route("/users", methods=['GET'])
@flask_login.login_required
def users():
        uid = getUserIdFromEmail(flask_login.current_user.id)
        recIdList = getReccomendedFriends(uid)
        recNameList = []
        topScoreList = getTopUsers()
        topNameList = []
        for i in recIdList:
                recName = (getNameFromId(i[0]))
                recNameList.append(recName[0][0] + " " + recName[0][1])

        for i in topScoreList:
                topName = (getNameFromId(i[0]))
                topNameList.append([topName[0][0] + " " + topName[0][1],i[1]])
                
        return render_template('users.html', userslist=getUsers(), recList=recNameList, topList = topNameList)

@app.route("/users", methods=['POST'])
def add_friend():

	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		newfriend = request.form.get('addfriend')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('users'))
	cursor = conn.cursor()
	email = getEmailfromGetUsers(newfriend)
	friendId = getUserIdFromEmail(email)
	test =  checkExistingFriend(uid, friendId)
	if test:
		cursor.execute(('''INSERT INTO Friends (friend_1, friend_2) VALUES ('{0}', '{1}')'''.format(uid,friendId)))
		conn.commit()
		return flask.redirect(flask.url_for('friends'))

	else:
		print("invalid fields")
		return flask.redirect(flask.url_for('users'))

def get_top_tags():
        cursor = conn.cursor()
        cursor.execute("SELECT tname FROM Tags T_2 GROUP BY T_2.tname HAVING COUNT(photo_id) = (SELECT MAX(c) from (SELECT COUNT(T.photo_id) as c FROM Tags T GROUP BY T.tname)as placeHold)")
        
        ret_val =  cursor.fetchall()
        tag_list = []
        for i in ret_val:
                tag_list.append(i[0])
        
        return tag_list

@app.route("/yourphotos", methods=['GET','POST'])
@flask_login.login_required
def your_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		tags = request.form.get('tagsearch')
		
		albumName = request.form.get('album')
		if(tags == ""):
			
			if (albumName == "All albums"):
				
				return render_template('yourphotos.html', photos=getUsersPhotos(uid), albums=getUsersAlbumNames(uid), base64=base64)
			else:
				albumId = getAlbumIdFromUidName(uid, albumName)[0][0]
				albumPhotos = getAlbumPhotos(albumId)
				
			return render_template('yourphotos.html', photos=albumPhotos, albums=getUsersAlbumNames(uid), base64=base64)

		else:
			tagsList = getTagsListFromString(tags)
			taggedPhotos = []
			
			if (albumName == "All albums"):
				
				for tag in tagsList:
					photos = getUserTaggedPhotos(uid,tag)
					
					for photo in photos:
						
						taggedPhotos.append(photo)
				
				taggedPhotos = removePhotoDupe(taggedPhotos)
				
				return render_template('yourphotos.html', photos=taggedPhotos, albums=getUsersAlbumNames(uid), base64=base64)
			else:

				albumId = getAlbumIdFromUidName(uid, albumName)[0][0]
				for tag in tagsList:
					photos = getAlbumTaggedPhotos(albumId, tag)
					
					for photo in photos:
						
						taggedPhotos.append(photo)
				
				taggedPhotos = removePhotoDupe(taggedPhotos)
				return render_template('yourphotos.html', photos=taggedPhotos, albums=getUsersAlbumNames(uid), base64=base64)

			
	else:

		return render_template('yourphotos.html', photos=getUsersPhotos(uid), albums=getUsersAlbumNames(uid), base64=base64)

def checkLiked(pid, uid):
        cursor = conn.cursor()
        if(cursor.execute("SELECT photo_id FROM Likes WHERE photo_id ='{0}' AND user_id='{1}'".format(pid,uid))):
                return True
        else:
                return False

def checkOwnComment(pid, uid):
        cursor = conn.cursor()
        if(cursor.execute("SELECT photo_id FROM Photos WHERE photo_id ='{0}' AND user_id='{1}'".format(pid,uid))):
                return True
        else:
                return False
@app.route("/allphotos", methods=['GET','POST'])
def all_photos():
        try:
                uid = getUserIdFromEmail(flask_login.current_user.id)
                loggedin = True
                rec_photos_val = getRecPhotos(uid)
                #rec_photos_val = False
        except:
                print("user not found")
                loggedin = False
                rec_photos_val = False
        if request.method == 'POST':
                likes = request.form.get('like')
                if(likes is not None and loggedin): 
                        if(checkLiked(likes,uid)):
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM Likes WHERE photo_id = '{0}' AND user_id = '{1}'".format(likes,uid))
                                conn.commit()
                                return render_template('allphotos.html', likecount=getLikes, photos=getPhotosDefault(), rec_photos = rec_photos_val, albums=getAlbumsByUsers(), tagList = get_top_tags(), base64=base64)
                        else:
                                cursor = conn.cursor()
                                cursor.execute(('''INSERT INTO Likes (photo_id, user_id) VALUES ('{0}', '{1}')'''.format(likes,uid)))
                                conn.commit()
                                return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(), rec_photos = rec_photos_val,albums=getAlbumsByUsers(), tagList = get_top_tags(), base64=base64)
                comment = request.form.get('comment')
                pid = request.form.get('submitcomment')
                if(pid is not None):
                        if(loggedin):
                                if(checkOwnComment(pid,uid)):
                                        return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(),rec_photos = rec_photos_val, albums=getAlbumsByUsers(), tagList = get_top_tags(), base64=base64)
                                else:
                                        cursor = conn.cursor()
                                        cursor.execute(('''INSERT INTO comments (user_id, photo_id, text) VALUES ('{0}', '{1}', '{2}')'''.format(uid,pid,comment)))
                                        conn.commit()
                                        return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(),rec_photos = rec_photos_val, albums=getAlbumsByUsers(), tagList = get_top_tags(), base64=base64)
                        else:
                                cursor = conn.cursor()
                                cursor.execute(('''INSERT INTO comments (photo_id, text) VALUES ('{0}', '{1}')'''.format(pid,comment)))
                                conn.commit()
                                return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(), rec_photos = rec_photos_val,albums=getAlbumsByUsers(), tagList = get_top_tags(), base64=base64)
                tags = request.form.get('tagsearch')
                albumId = request.form.get('album')
                tags_from_button = request.form.get('tagbutton')
                if tags == "" and tags_from_button != None:
                        tags = tags_from_button
                if(tags == ""):
                        
                        if (albumId == "All albums"):
                                return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(), rec_photos = rec_photos_val,albums=getAlbumsByUsers(),tagList = get_top_tags(), base64=base64)
                        else:
                                albumId = getAlbumIdFromAllList(request.form.get('album'))
                                print(albumId)
                                albumPhotos = getAlbumPhotos(albumId)
				
                        return render_template('allphotos.html', likecount=getLikes,photos=albumPhotos, albums=getAlbumsByUsers(),rec_photos = rec_photos_val,tagList = get_top_tags(), base64=base64)

                else:
                        tagsList = getTagsListFromString(tags)
                        taggedPhotos = []
			
                        if (albumId == "All albums"):	
                                for tag in tagsList:
                                        photos = getAllTaggedPhotos(tag)
					
                                        for photo in photos:
						
                                                taggedPhotos.append(photo)
				
                                taggedPhotos = removePhotoDupe(taggedPhotos)
				
                                return render_template('allphotos.html', likecount=getLikes,photos=taggedPhotos, albums=getAlbumsByUsers(), rec_photos = rec_photos_val, tagList = get_top_tags(), base64=base64)
                        else:
                                albumId = getAlbumIdFromAllList(request.form.get('album'))
                                for tag in tagsList:
                                        photos = getAlbumTaggedPhotosDefault(albumId, tag)
					
                                        for photo in photos:
						
                                                taggedPhotos.append(photo)
				
                                taggedPhotos = removePhotoDupe(taggedPhotos)
				
                                return render_template('allphotos.html', likecount=getLikes,photos=taggedPhotos, albums=getAlbumsByUsers(), rec_photos = rec_photos_val, tagList = get_top_tags(),base64=base64)
			
        else:
                return render_template('allphotos.html', likecount=getLikes,photos=getPhotosDefault(), albums=getAlbumsByUsers(), rec_photos = rec_photos_val,tagList = get_top_tags(), base64=base64)



@app.route("/deletedphoto", methods=['POST'])
def delete_photo():
	photoId = request.form.get('deleteButton')
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photoId))
	conn.commit()
	return render_template('deletedphoto.html')

@app.route("/deletedalbum", methods=['POST'])
def delete_album():
	albumName = request.form.get('albumdel')
	if(albumName == "-"):
		return flask.redirect(flask.url_for('your_photos'))
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		albumId = getAlbumIdFromUidName(uid, albumName)[0][0]
		print(albumName)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Albums WHERE albums_id = '{0}'".format(albumId))
		conn.commit()
		return render_template('deletedalbum.html')


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welcome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
