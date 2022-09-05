USE photoshare2;
DELETE FROM Users;
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Daniel', 'Zhou', 'dpz@bu.edu', '2000-07-28', 'dpz'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Bob', 'Melvin', 'bm@bu.edu', '2000-07-20','bm'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Mookie', 'Betts', 'mb@bu.edu', '2000-03-29','mb'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Rafael', 'Devers', 'rf@bu.edu', '2000-07-28','rf'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Chris', 'Sale', 'cs@bu.edu', '2000-07-28','cs'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Randy', 'Johnson', 'rj@bu.edu', '2000-07-28','rj'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Alex', 'Cora', 'ac@bu.edu', '2000-07-28','ac'); 
INSERT INTO Users (first_name, last_name, email, birth_date, password) VALUES ('Alex', 'Verdugo', 'ac@bu.edu', '2000-07-28','av'); 

/*
INSERT INTO Albums (albums_id, name, date, user_id) VALUES (1, 'a', '2000-06-28',3);
INSERT INTO Photos (albums_id, user_id) VALUES (1, 3);
INSERT INTO Photos (albums_id, user_id) VALUES (1, 3);
INSERT INTO Photos (albums_id, user_id) VALUES (1, 3);
INSERT INTO Photos (albums_id, user_id) VALUES (1, 3);
INSERT INTO Photos (albums_id, user_id) VALUES (1, 3);

INSERT INTO Tags(tname, photo_id) VALUES (1, 1);
INSERT INTO Tags(tname, photo_id) VALUES (2, 2);
INSERT INTO Tags(tname, photo_id) VALUES (3, 3);
INSERT INTO Tags(tname, photo_id) VALUES (4, 4);
INSERT INTO Tags(tname, photo_id) VALUES (5, 5);
INSERT INTO Tags(tname, photo_id) VALUES (1, 2);
INSERT INTO Tags(tname, photo_id) VALUES (4, 3);
*/

