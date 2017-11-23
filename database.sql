drop table if exists person;
drop table if exists profile;
drop table if exists AI;
drop table if exists session;
drop table if exists convos;

create table person( #basic profile information to start account
	personId int auto_increment not null primary key,
	name varchar(50) not null,
	lang varchar(50) not null, #language person want to learn
	username varchar(50) not null, #wellesley alias
	password varchar(100) not null, #password
	age int,
);

create table profile( #detailed profile info from onboarding survey
	personId int not null,
	yearsLearned int,
	learningStyle enum('class','online','speaking'),
	proficiencyScore int not null,
	score int not null default 0,
	timeActive int not null default 0, #measured in days
	proPic varchar(100), #profile picture file path
	#survey questions:
	faveSport enum('a','b','c','d'),
	faveShow enum('a','b','c','d'),
	faveHobby enum('a','b','c','d'),
	faveFood enum('a','b','c','d'),
	faveCountry enum('a','b','c','d')

	foreign key (personId) references person(personId) on delete restrict on update restrict
);

create table AI( #stores all possible conversations
	questionId int auto_increment not null primary key,
	categoryId int not null, #allows multiple questions to be grouped
	categoryType varchar(50), #topic of conversation
	lang varchar(50) not null,
	questionText varchar(100) not null, #question the AI will ask
);

create table sessions( #stores each person's sessions
	sessionId int auto_increment not null primary key,
	personId int not null,
	convoId int not null, #each conversation stores one question and one answer

	foreign key (personId) references person(personId) on delete restrict on update restrict,
	foreign key (convoId) references convos(convoId) on delete restrict on update restrict
);

create table convos( #stores each conversation a user has
	convoId int auto_increment not null primary key,
	sessionId int not null,

	questionId int not null,
	answerText varchar(100) not null, #store file path for audio answer

	foreign key (sessionId) references sessions(sessionId) on delete restrict on update restrict,
	foreign key (questionId) references AI(questionId) on delete restrict on update restrict
);
