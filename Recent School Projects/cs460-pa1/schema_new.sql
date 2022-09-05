CREATE DATABASE IF NOT EXISTS photoshare2;
USE photoshare2;
DROP TABLE IF EXISTS Photos CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users(
 user_id INTEGER AUTO_INCREMENT,
 first_name VARCHAR(100) NOT NULL,
 last_name VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL,
 birth_date DATE NOT NULL,
 hometown VARCHAR(100),
 gender VARCHAR(100),
 password VARCHAR(100) NOT NULL,
 PRIMARY KEY (user_id)
 );

 CREATE TABLE Friends(
 friend_1 INTEGER,
 friend_2 INTEGER,
 PRIMARY KEY (friend_1, friend_2),
 FOREIGN KEY (friend_1)
 REFERENCES Users(user_id),
 FOREIGN KEY (friend_2)
 REFERENCES Users(user_id)
 /*CONSTRAINT same_friend CHECK (friend_1 <> friend_2)*/
);

CREATE TABLE Albums(
 albums_id INTEGER AUTO_INCREMENT,
 name VARCHAR(100),
 date DATE,
 user_id INTEGER NOT NULL,
 PRIMARY KEY (albums_id),
 FOREIGN KEY (user_id)
 REFERENCES Users(user_id)
);



CREATE TABLE Photos(
 photo_id INTEGER AUTO_INCREMENT,
 caption VARCHAR(200),
 data LONGBLOB,
 albums_id INTEGER NOT NULL,
 user_id INTEGER NOT NULL,
 PRIMARY KEY (photo_id),
 FOREIGN KEY (albums_id) REFERENCES Albums (albums_id) ON DELETE CASCADE,
 FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);
CREATE TABLE Tags(
 tname VARCHAR(100),
 photo_id INTEGER,
 PRIMARY KEY (tname, photo_id),
 FOREIGN KEY(photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
);
/*
CREATE TABLE Tagged(
 photo_id INTEGER,
 tag_id INTEGER,
 PRIMARY KEY (photo_id, tag_id),
 FOREIGN KEY(photo_id)
 REFERENCES Photos (photo_id),
 FOREIGN KEY(tag_id)
 REFERENCES Tags (tag_id)
);
*/
CREATE TABLE Comments(
 comment_id INTEGER AUTO_INCREMENT,
 user_id INTEGER,
 photo_id INTEGER NOT NULL,
 text VARCHAR (100),
 date DATE,
 PRIMARY KEY (comment_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id)
 );

CREATE TABLE Likes(
 photo_id INTEGER,
 user_id INTEGER,
 PRIMARY KEY (photo_id,user_id),
 FOREIGN KEY (photo_id)
 REFERENCES Photos (photo_id),
 FOREIGN KEY (user_id)
 REFERENCES Users (user_id)
);
