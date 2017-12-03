SET FOREIGN_KEY_CHECKS=0; -- ignore foreign key checks when initializing tables

drop table if exists convos;
drop table if exists category;
drop table if exists sessions;
drop table if exists AI;
drop table if exists profile;
drop table if exists account;

SET FOREIGN_KEY_CHECKS=1;

create table account( -- basic profile information to start account
	userId int auto_increment not null primary key,
	name varchar(50) not null,
	username varchar(50) not null, -- wellesley alias
	password varchar(100) not null -- hashed password
);

create table profile( -- detailed profile info from onboarding survey
	userId int not null,
	yearsLearned int not null,
	birthday Date not null,
	nativeLang varchar(50), -- persons native language
	nation varchar(50),
	-- proficiencyScore int not null, we are not demostrating this for the project
	points int not null default 0, -- points earned using the application
	timeActive int not null default 0, -- measured in days
	-- proPic varchar(100), profile picture file path. we can get rid of this if audio file works
	-- survey questions:
	faveSport enum('swimming','table tennis','basketball', 'running', 'sleeping','yoga'),
	faveShow enum('Star Trek','Titanic','Modern Family','News'),
	faveHobby enum('Drawing','Singing','Playing music','Hiking'),
	faveFood enum('Chinese food','American food','Indian food','Mexican food'),
	faveCountry enum('America','UK','France','China'),

	foreign key (userId) references account(userId) on delete cascade on update cascade
);

create table category(
	categoryId int auto_increment not null primary key,
	categoryType varchar(50) -- topic of conversation
);

insert into category (categoryType) values ('school');
insert into category (categoryType) values ('food');
insert into category (categoryType) values ('hobby');

create table AI( -- stores all possible conversations
	questionId int auto_increment not null primary key,
	categoryId int not null, -- allows multiple questions to be grouped
	questionText varchar(100) not null, -- question the AI will ask
	foreign key (categoryId) references category(categoryId) on delete cascade on update cascade
);

insert into AI (categoryId, questionText) values (1, 'Tell me about your school. Do you like it?');
insert into AI (categoryId, questionText) values (1, "What's your favorite subject? Why do you like it so much?");
insert into AI (categoryId, questionText) values (1, "What's your favorite book? What makes it so fascinating?");
insert into AI (categoryId, questionText) values (1, 'So...what do you imagine yourself doing in 50 years?');
insert into AI (categoryId, questionText) values (2, "What's your favorite dish? Describe it to be coz I want to try.");
insert into AI (categoryId, questionText) values (2, 'Do you like to cook? What kind of food can you cook?');
insert into AI (categoryId, questionText) values (2, 'What would you do to keep a healthy lifestyle?');
insert into AI (categoryId, questionText) values (3, 'What do you like to do in your free time?');
insert into AI (categoryId, questionText) values (3, "What's your favorite sports? What's the secret of being good at it?");

create table convos( -- stores each conversation a user has
	convoId int auto_increment not null primary key,
	-- sessionId int not null,
	categoryId int not null, #so we can join them to give feedback
	-- questionId int not null,
	answerText varchar(100) not null, #store file path for audio answer - one audio file for entire conversation
	-- userId int not null,
	-- foreign key (sessionId) references sessions(sessionId) on delete cascade on update cascade,
	-- foreign key (userId) references account(userId) on delete cascade on update cascade,
	foreign key (categoryId) references category(categoryId) on delete cascade on update cascade
);

-- create table sessions( #stores each persons sessions
-- 	sessionId int auto_increment not null primary key,
-- 	userId int not null,
-- 	-- convoId int not null, #each conversation stores one question and one answer

-- 	foreign key (userId) references account(userId) on delete cascade on update cascade
-- 	-- foreign key (convoId) references convos(convoId) on delete cascade on update cascade
-- );

#erase this later:
-- insert into account (name, username, password) values ('Mojia', 'mshen2', '1234')
