
CREATE TABLE Cities (
    city_id INT PRIMARY KEY IDENTITY(1,1),
    city_name VARCHAR(100) NOT NULL,
   
);






CREATE TABLE Institutions (
    institution_id INT PRIMARY KEY IDENTITY(1,1),
    institution_name VARCHAR(100) NOT NULL,
    institution_type VARCHAR(50) NOT NULL, -- University, High School vb.
    city_id INT NOT NULL,

    -- Kýsýtlamadan önce virgül olmalý, sonunda noktalý virgül parantez dýþýnda olmalý
    CONSTRAINT FK_Institution_City FOREIGN KEY (city_id) 
        REFERENCES Cities(city_id)
);



CREATE TABLE Categories (
    category_id INT PRIMARY KEY IDENTITY(1,1),
    category_name VARCHAR(100) NOT NULL,
    
    min_altitude INT NOT NULL,

   
);











CREATE TABLE Teams (
    team_id INT PRIMARY KEY IDENTITY(1,1), -- Benzersiz takým ID
    team_name VARCHAR(100) NOT NULL,       -- Takým adý
    institution_id INT NOT NULL,           -- Hangi kuruma baðlý? (FK)
    category_id INT NOT NULL,-- Ýliþkilerin Tanýmlanmasý (Foreign Keys)

    CONSTRAINT FK_Team_Institution FOREIGN KEY (institution_id) 

        REFERENCES Institutions(institution_id),

        

    CONSTRAINT FK_Team_Category FOREIGN KEY (category_id) 

        REFERENCES Categories(category_id));





CREATE TABLE Roles(
role_id INT PRIMARY KEY IDENTITY (1,1),
role_name VARCHAR (50) NOT NULL,
)

CREATE TABLE Members (
member_name VARCHAR(50) NOT NULL,
member_id INT PRIMARY KEY IDENTITY(1,1),

role_id INT NOT NULL,
team_id INT NOT NULL,



 CONSTRAINT FK_Member_Role FOREIGN KEY (role_id) 

        REFERENCES Roles(role_id),




    CONSTRAINT FK_Member_Team FOREIGN KEY (team_id) 

        REFERENCES Teams(team_id));




CREATE TABLE Manufecturers(
manuf_id INT PRIMARY KEY IDENTITY (1,1),
manuf_name VARCHAR(50) NOT NULL,
);



CREATE TABLE Motors(
motor_id INT PRIMARY KEY IDENTITY (1,1),
motor_name VARCHAR(50) NOT NULL,
thrust_pow INT NOT NULL,
manuf_id INT NOT NULL,

CONSTRAINT FK_Motor_Manufacturer FOREIGN KEY (manuf_id)
REFERENCES Manufecturers (manuf_id));




CREATE TABLE Rockets(

rocket_id INT PRIMARY KEY IDENTITY (1,1),
rocket_name VARCHAR(100) NOT NULL,

motor_id INT NOT NULL,
team_id INT NOT NULL,
category_id INT NOT NULL,



CONSTRAINT FK_Rocket_Motor FOREIGN KEY (motor_id)
REFERENCES Motors (motor_id),

CONSTRAINT FK_Rocket_Team FOREIGN KEY (team_id)
REFERENCES Teams (team_id)





);

CREATE TABLE Payloads (
    payload_id INT PRIMARY KEY IDENTITY(1,1),
    payload_name VARCHAR(100) NOT NULL,
    payload_weight FLOAT,           -- Yükün aðýrlýðý
    mission_purpose VARCHAR(MAX),   -- Görev amacý (Uzun metin için MAX)
    rocket_id INT UNIQUE NOT NULL,  -- Hangi rokette? (Her roketin 1 yükü olmasý için UNIQUE)

    CONSTRAINT FK_Payload_Rocket FOREIGN KEY (rocket_id)
        REFERENCES Rockets(rocket_id)
);




-- Önce aþama isimlerini tanýmlayalým
CREATE TABLE Stages (
    stage_id INT PRIMARY KEY IDENTITY(1,1),
    stage_name VARCHAR(50) NOT NULL -- 'OTR', 'KTR', 'Final' gibi
);

-- Hangi takým hangi aþamayý geçti?
CREATE TABLE Team_Progress (
    progress_id INT PRIMARY KEY IDENTITY(1,1),
    team_id INT NOT NULL,
    stage_id INT NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'Passed', 'Failed', 'Pending'
    score INT,                   -- O aþamadan aldýðý puan
    pass_date DATETIME DEFAULT GETDATE(),

    CONSTRAINT FK_Progress_Team FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    CONSTRAINT FK_Progress_Stage FOREIGN KEY (stage_id) REFERENCES Stages(stage_id)
);

CREATE TABLE Referees(

ref_id INT PRIMARY KEY IDENTITY(1,1),
ref_name VARCHAR(50) NOT NULL,
rocket_id INT NOT NULL,

CONSTRAINT FK_Ref_Rocket FOREIGN KEY (rocket_id)
REFERENCES Rockets (rocket_id)




);





CREATE TABLE Sponsors (
    sponsor_id INT PRIMARY KEY IDENTITY(1,1),
    sponsor_name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),          -- Sektör (Savunma, Teknoloji vb.)
    contact_email VARCHAR(100),     -- Ýletiþim e-postasý
    contribution_type VARCHAR(50)   -- Destek tipi (Maddi, Teknik, Lojistik)
);

-- Cities
INSERT INTO Cities (city_name) VALUES
('Ankara'), ('Ýstanbul'), ('Ýzmir'), ('Konya'), ('Bursa');

-- Institutions
INSERT INTO Institutions (institution_name, institution_type, city_id) VALUES
('Orta Doðu Teknik Üniversitesi', 'University', 1),
('Ýstanbul Teknik Üniversitesi', 'University', 2),
('Ýzmir Yüksek Teknoloji Enstitüsü', 'University', 3),
('Selçuk Üniversitesi', 'University', 4),
('Uludað Üniversitesi', 'University', 5),
('Ankara Fen Lisesi', 'High School', 1),
('Robert Kolej', 'High School', 2);

-- Categories
INSERT INTO Categories (category_name, min_altitude) VALUES
('Lisans', 1000),
('Lisansüstü', 3000),
('Lise', 500),
('Uluslararasý', 5000);

-- Teams
INSERT INTO Teams (team_name, institution_id, category_id) VALUES
('ODTÜ Roket Topluluðu', 1, 1),
('ÝTÜ Çekirdek', 2, 1),
('AeroIYTE', 3, 2),
('Selçuk Uzay', 4, 1),
('Uludað Göktaþý', 5, 1),
('AFL Roket Kulübü', 6, 3),
('Robert Kolej Rocketry', 7, 3);

-- Roles
INSERT INTO Roles (role_name) VALUES
('Takým Kaptaný'),
('Yazýlým Mühendisi'),
('Mekanik Tasarýmcý'),
('Aviyonik Uzmaný'),
('Yük Sistemi Sorumlusu');

-- Members
INSERT INTO Members (member_name, role_id, team_id) VALUES
('Ahmet Yýlmaz', 1, 1),
('Elif Kaya', 2, 1),
('Burak Demir', 3, 1),
('Zeynep Arslan', 4, 1),
('Mert Çelik', 1, 2),
('Selin Öztürk', 2, 2),
('Tolga Aydýn', 3, 2),
('Deniz Þahin', 5, 3),
('Kerem Polat', 1, 3),
('Nihan Güneþ', 4, 4),
('Ege Koç', 3, 5),
('Ayþe Kurt', 1, 6),
('Can Erdoðan', 2, 7);

-- Manufecturers
INSERT INTO Manufecturers (manuf_name) VALUES
('Cesaroni Technology'),
('Aerotech'),
('Klima-Buk'),
('Roketsan');

-- Motors
INSERT INTO Motors (motor_name, thrust_pow, manuf_id) VALUES
('Pro54-4G', 360, 1),
('J570W', 570, 2),
('K1050', 1050, 2),
('L1170', 1170, 3),
('RS-100', 850, 4);

-- Rockets
INSERT INTO Rockets (rocket_name, motor_id, team_id, category_id) VALUES
('Feniks-I', 3, 1, 1),
('ÝTÜ Orion', 4, 2, 1),
('Hyperion', 5, 3, 2),
('Selçuk-1', 2, 4, 1),
('Göktaþý-A', 1, 5, 1),
('AeroStar', 1, 6, 3),
('RC Vega', 2, 7, 3);

-- Payloads
INSERT INTO Payloads (payload_name, payload_weight, mission_purpose, rocket_id) VALUES
('AtmosferSensörü', 0.45, 'Sýcaklýk ve basýnç ölçümü', 1),
('KameraMod', 0.60, 'Apogee aný görüntü kaydý', 2),
('CanSat-Pro', 0.35, 'Serbest býrakma ve glide testi', 3),
('GPS-Beacon', 0.20, 'Konum takip ve kurtarma sistemi', 4),
('BiyoDeney', 0.55, 'Mikrogravite biyoloji deneyi', 5),
('EduPay-1', 0.15, 'Lise eðitim verisi toplama', 6),
('SpectroScan', 0.40, 'UV-görünür spektral analiz', 7);

-- Stages
INSERT INTO Stages (stage_name) VALUES
('OTR'), ('KTR'), ('Final');

-- Team_Progress
INSERT INTO Team_Progress (team_id, stage_id, status, score) VALUES
(1, 1, 'Passed', 88),
(1, 2, 'Passed', 91),
(1, 3, 'Pending', NULL),
(2, 1, 'Passed', 84),
(2, 2, 'Passed', 79),
(2, 3, 'Pending', NULL),
(3, 1, 'Passed', 95),
(3, 2, 'Passed', 92),
(3, 3, 'Passed', 89),
(4, 1, 'Passed', 76),
(4, 2, 'Failed', 48),
(5, 1, 'Passed', 81),
(5, 2, 'Pending', NULL),
(6, 1, 'Passed', 70),
(7, 1, 'Failed', 44);

-- Referees
INSERT INTO Referees (ref_name, rocket_id) VALUES
('Prof. Dr. Haluk Aras', 1),
('Doç. Dr. Seda Yýldýz', 2),
('Dr. Öðr. Ü. Murat Kaplan', 3),
('Prof. Dr. Haluk Aras', 4),
('Arþ. Gör. Banu Demiral', 5),
('Doç. Dr. Seda Yýldýz', 6),
('Dr. Öðr. Ü. Murat Kaplan', 7);

-- Sponsors
INSERT INTO Sponsors (sponsor_name, industry, contact_email, contribution_type) VALUES
('Roketsan A.Þ.', 'Savunma', 'info@roketsan.com.tr', 'Teknik'),
('Türk Havacýlýk ve Uzay Sanayii', 'Havacýlýk', 'kurumsal@tai.com.tr', 'Maddi'),
('Aselsan A.Þ.', 'Savunma', 'sponsorluk@aselsan.com.tr', 'Maddi'),
('Türk Telekom', 'Teknoloji', 'kurumsal@turktelekom.com.tr', 'Lojistik'),
('Boeing Türkiye', 'Havacýlýk', 'turkey@boeing.com', 'Teknik');



DELETE FROM Rockets
DELETE FROM Motors
DELETE FROM Manufecturers
DELETE FROM Referees
DELETE FROM Payloads
DELETE FROM Sponsors
DELETE FROM Teams
DELETE FROM Members
DELETE FROM Team_Progress
DELETE FROM Roles
DELETE FROM Institutions
DELETE FROM Categories
DELETE FROM Cities
DELETE FROM Stages





SELECT * FROM Cities;
SELECT * FROM Institutions;
SELECT * FROM Categories;
SELECT * FROM Teams;
SELECT * FROM Roles;
SELECT * FROM Members;
SELECT * FROM Manufecturers;
SELECT * FROM Motors;
SELECT * FROM Rockets;
SELECT * FROM Payloads;
SELECT * FROM Stages;
SELECT * FROM Team_Progress;
SELECT * FROM Referees;
SELECT * FROM Sponsors;



TRUNCATE TABLE Referees;
TRUNCATE TABLE Payloads;
TRUNCATE TABLE Rockets;
TRUNCATE TABLE Motors;
TRUNCATE TABLE Manufecturers;
TRUNCATE TABLE Members;
TRUNCATE TABLE Team_Progress;
TRUNCATE TABLE Teams;
TRUNCATE TABLE Roles;
TRUNCATE TABLE Institutions;
TRUNCATE TABLE Categories;
TRUNCATE TABLE Cities;

EXEC sp_MSforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all";
EXEC sp_MSforeachtable "TRUNCATE TABLE ?";
EXEC sp_MSforeachtable "ALTER TABLE ? CHECK CONSTRAINT all";
