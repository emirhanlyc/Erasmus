
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
);

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


INSERT INTO Cities (city_name) 
VALUES 
('Ankara'), 
('Ýstanbul'), 
('Ýzmir'), 
('Konya'), 
('Bursa');

SELECT * FROM Cities;


INSERT INTO Institutions (institution_name, institution_type, city_id) 
VALUES 
('Orta Doðu Teknik Üniversitesi', 'University', 1), -- 1: Ankara
('Ýstanbul Teknik Üniversitesi', 'University', 2),  -- 2: Ýstanbul
('Ege Üniversitesi', 'University', 3),             -- 3: Ýzmir
('Selçuk Üniversitesi', 'University', 4),           -- 4: Konya
('Bursa Teknik Üniversitesi', 'University', 5);     -- 5: Bursa

SELECT * FROM Institutions;




INSERT INTO Categories (category_name, min_altitude) 
VALUES 
('Low', 1500),
('Medium', 3000),
('High', 6000),
('Dual Separate', 4500);

SELECT * FROM Categories

INSERT INTO Teams (team_name, institution_id, category_id) 
VALUES 
('Anatolian Rocketry Group', 1, 2),    -- Connected to METU, Mid-Altitude
('Bosphorus Aerospace', 2, 3),        -- Connected to ITU, High-Altitude
('Aegean Rocketry Team', 3, 1),       -- Connected to Ege Uni, High School/Entry
('Steppe Technology', 4, 4),          -- Connected to Selcuk Uni, Challenging Mission
('Skyline Space Systems', 5, 2);      -- Connected to Bursa Tech, Mid-Altitude


SELECT * FROM Teams;




-- 1. BAÐIMSIZ TABLOLAR (Önce bunlar)
INSERT INTO Roles (role_name) VALUES 
('Team Leader'), ('Avionics'), ('Mechanical'), ('Recovery'), ('Propulsion');

INSERT INTO Manufecturers (manuf_name) VALUES 
('Cesaroni'), ('Aerotech'), ('Roxtek'), ('SkyDragon');

INSERT INTO Stages (stage_name) VALUES 
('PDR'), ('CDR'), ('VHR'), ('Final');

INSERT INTO Sponsors (sponsor_name, industry, contribution_type) VALUES 
('SpaceX', 'Aerospace', 'Technical'), 
('TechCorp', 'Electronics', 'Financial');


-- 2. MOTORS (Manufacturer'a baðlý)
INSERT INTO Motors (motor_name, thrust_pow, manuf_id) VALUES 
('Pro98-6G', 5000, 1), 
('L1170-P', 4200, 2);


-- 3. MEMBERS (Roles ve Teams'e baðlý)
-- 3. MEMBERS Tablosu Ýçin Türkçe Veri Giriþi
-- Sýralama: member_name, role_id, team_id
-- (member_id otomatik atanacak)

INSERT INTO Members (member_name, role_id, team_id) VALUES 
-- 1. Takým: Anatolian Rocketry Group
('Ahmet Yýlmaz', 1, 1),   -- Team Leader
('Ayþe Kaya', 2, 1),      -- Avionics
('Mehmet Demir', 3, 1),   -- Mechanical
('Fatma Çelik', 4, 1),    -- Recovery
('Mustafa Þahin', 5, 1),  -- Propulsion

-- 2. Takým: Bosphorus Aerospace
('Zeynep Öztürk', 1, 2),  -- Team Leader
('Ali Yýldýz', 2, 2),     -- Avionics
('Elif Doðan', 3, 2),     -- Mechanical
('Burak Arslan', 5, 2),   -- Propulsion

-- 3. Takým: Aegean Rocketry Team
('Emre Can', 1, 3),       -- Team Leader
('Merve Aydýn', 3, 3),    -- Mechanical
('Hasan Koç', 4, 3),      -- Recovery

-- 4. Takým: Steppe Technology
('Deniz Polat', 1, 4),    -- Team Leader
('Kerem Bulut', 2, 4),    -- Avionics

-- 5. Takým: Skyline Space Systems
('Cemre Erdem', 1, 5),    -- Team Leader
('Ozan Kýlýç', 5, 5);     -- Propulsion


-- 4. ROCKETS (Motors, Teams ve Categories'e baðlý)
INSERT INTO Rockets (rocket_name, motor_id, team_id, category_id) VALUES 
('Phoenix Alpha', 1, 1, 2), 
('Icarus II', 2, 2, 3);


-- 5. ROKETLERE VE SÜREÇLERE BAÐLI TABLOLAR (En son bunlar)
INSERT INTO Payloads (payload_name, payload_weight, mission_purpose, rocket_id) VALUES 
('CubeSat-V1', 4.5, 'Atmospheric Sensing', 1), 
('Bio-Module', 2.0, 'Seed Experiment', 2);

INSERT INTO Team_Progress (team_id, stage_id, status, score) VALUES 
(1, 1, 'Passed', 95), 
(2, 1, 'Passed', 92);

INSERT INTO Referees (ref_name, rocket_id) VALUES 
('Dr. Alan Grant', 1), 
('Sarah Connor', 2);






-- 1. Organizasyon ve Lokasyon Verileri
SELECT * FROM Cities;
SELECT * FROM Institutions;
SELECT * FROM Sponsors;

-- 2. Yarýþma ve Takým Yapýsý
SELECT * FROM Categories;
SELECT * FROM Teams;
SELECT * FROM Roles;
SELECT * FROM Members;

-- 3. Teknik Detaylar (Motor ve Roket)
SELECT * FROM Manufecturers;
SELECT * FROM Motors;
SELECT * FROM Rockets;
SELECT * FROM Payloads;

-- 4. Süreç ve Deðerlendirme
SELECT * FROM Stages;
SELECT * FROM Team_Progress;
SELECT * FROM Referees;