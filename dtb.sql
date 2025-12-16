CREATE DATABASE QLToDanPho;
Use QlToDanPho;

DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS COMMENDATION_NOTIFICATION CASCADE;
DROP TABLE IF EXISTS COMMENDATION_DECISION CASCADE;
DROP TABLE IF EXISTS COMMENDATION_PROPOSAL CASCADE;
DROP TABLE IF EXISTS AWARD CASCADE;
DROP TABLE IF EXISTS TEMPORARY_ABSENCE CASCADE;
DROP TABLE IF EXISTS TEMPORARY_RESIDENCE CASCADE;
DROP TABLE IF EXISTS CITIZENSHIP_HISTORY CASCADE;
DROP TABLE IF EXISTS HOUSEHOLD_BOOK CASCADE;
DROP TABLE IF EXISTS CITIZEN CASCADE;
DROP TABLE IF EXISTS ADMINISTRATIVE_UNIT CASCADE;

-- 1. Table ADMINISTRATIVE_UNIT 
CREATE TABLE ADMINISTRATIVE_UNIT (
    Unit_ID VARCHAR(10) PRIMARY KEY,
    Unit_Name VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    Unit_Type VARCHAR(50) NOT NULL -- 'Ward/Commune', 'District', 'Commendation_Agency'
);

-- 2. Table CITIZEN 
CREATE TABLE CITIZEN (
    CCCD_ID VARCHAR(20) PRIMARY KEY,
    Full_Name VARCHAR(100) NOT NULL,
    Date_of_Birth DATE NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    Birth_Registration_Place VARCHAR(200) NOT NULL,
    Place_of_Origin VARCHAR(200) NOT NULL,
    Ethnicity VARCHAR(50) NOT NULL,
    Religion VARCHAR(50),
    Nationality VARCHAR(50) DEFAULT 'Vietnam',
    Marital_Status VARCHAR(50), -- 'Single', 'Married', 'Divorced'
    Occupation VARCHAR(100), 
    Education_Level VARCHAR(50), 
    Permanent_Address VARCHAR(200) NOT NULL,
    Current_Residence VARCHAR(200) NOT NULL,
    Residence_Status VARCHAR(50) DEFAULT 'Permanent' CHECK (Residence_Status IN ('Permanent', 'Temporary_Resident', 'Temporary_Absent')), -- General status
    Relationship_to_Head VARCHAR(50) NOT NULL,
    Blood_Type VARCHAR(10),
    Father_CCCD_ID VARCHAR(20),
    Mother_CCCD_ID VARCHAR(20),
    Spouse_CCCD_ID VARCHAR(20),
    Head_of_Household_CCCD_ID VARCHAR(20),
    Management_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID), 
    Date_of_Death DATE
);

-- 3. Table HOUSEHOLD_BOOK 
CREATE TABLE HOUSEHOLD_BOOK (
    Household_Book_ID VARCHAR(50) PRIMARY KEY,
    Head_of_Household_CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Permanent_Residence_Address VARCHAR(200) NOT NULL,
    Issue_Date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Number_of_Members INTEGER NOT NULL,
    Issuing_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID), 
    CONSTRAINT unique_head_of_household UNIQUE (Head_of_Household_CCCD_ID)
);

-- 4. Update link between CITIZEN and HOUSEHOLD_BOOK
ALTER TABLE CITIZEN ADD COLUMN Household_Book_ID VARCHAR(50) REFERENCES HOUSEHOLD_BOOK(Household_Book_ID);

-- 5. Table TEMPORARY_RESIDENCE
CREATE TABLE TEMPORARY_RESIDENCE (
    Temp_Residence_ID VARCHAR(50) PRIMARY KEY,
    CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Temporary_Address VARCHAR(200) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE,
    Registration_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID) 
);

-- 6. Table TEMPORARY_ABSENCE
CREATE TABLE TEMPORARY_ABSENCE (
    Temp_Absence_ID VARCHAR(50) PRIMARY KEY,
    CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Reason VARCHAR(200) NOT NULL,
    Destination VARCHAR(200), 
    Start_Date DATE NOT NULL,
    End_Date DATE,
    Registration_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID) 
);

-- 7. Table CITIZENSHIP_HISTORY
CREATE TABLE CITIZENSHIP_HISTORY (
    History_ID SERIAL PRIMARY KEY,
    CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Change_Type VARCHAR(100) NOT NULL, -- 'Marriage', 'Divorce', 'ID_Change', 'Residence_Change'
    Old_Content TEXT,
    New_Content TEXT,
    Change_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Performer_Name VARCHAR(100), -- Name or UserID of the person who entered/approved
    Performing_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID) 
);

-- 8. Table AWARD 
CREATE TABLE AWARD (
    Award_ID VARCHAR(50) PRIMARY KEY,
    Award_Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Criteria TEXT,
    Form VARCHAR(50) -- 'Medal', 'Certificate_of_Merit', 'Commendation_Letter'
);

-- 9. Table COMMENDATION_PROPOSAL
CREATE TABLE COMMENDATION_PROPOSAL (
    Proposal_ID VARCHAR(50) PRIMARY KEY,
    CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Award_ID VARCHAR(50) NOT NULL REFERENCES AWARD(Award_ID),
    Proposal_Date DATE NOT NULL,
    Proposing_Agency VARCHAR(100), -- Added property
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Pending', 'Approved', 'Rejected')),
    Approver_Name VARCHAR(100),
    Approval_Date DATE,
    Note TEXT
);

-- 10. Table COMMENDATION_DECISION 
CREATE TABLE COMMENDATION_DECISION (
    Decision_ID VARCHAR(50) PRIMARY KEY,
    Proposal_ID VARCHAR(50) NOT NULL REFERENCES COMMENDATION_PROPOSAL(Proposal_ID) UNIQUE,
    Decision_Date DATE NOT NULL,
    Issuing_Agency VARCHAR(100),
    Result VARCHAR(20) NOT NULL CHECK (Result IN ('Commended', 'Not_Commended')),
    Note TEXT
);

-- 11. Table COMMENDATION_NOTIFICATION 
CREATE TABLE COMMENDATION_NOTIFICATION (
    Notification_ID VARCHAR(50) PRIMARY KEY,
    CCCD_ID VARCHAR(20) NOT NULL REFERENCES CITIZEN(CCCD_ID),
    Title VARCHAR(100) NOT NULL, -- Added property
    Content TEXT NOT NULL,
    Sent_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Sent', 'Read'))
);

-- 12. Table users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'citizen', -- Expanded roles
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cccd_id VARCHAR(20) UNIQUE,
    Working_Unit_ID VARCHAR(10) REFERENCES ADMINISTRATIVE_UNIT(Unit_ID), -- Added: User's working unit
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'citizenship_manager', 'commendation_manager', 'citizen')),
    CONSTRAINT fk_users_citizen FOREIGN KEY (cccd_id) REFERENCES CITIZEN(CCCD_ID)
);

-- 13. Add supplementary Foreign Keys to CITIZEN (Father, Mother, Spouse)
ALTER TABLE CITIZEN 
ADD CONSTRAINT fk_citizen_father FOREIGN KEY (Father_CCCD_ID) REFERENCES CITIZEN(CCCD_ID),
ADD CONSTRAINT fk_citizen_mother FOREIGN KEY (Mother_CCCD_ID) REFERENCES CITIZEN(CCCD_ID),
ADD CONSTRAINT fk_citizen_spouse FOREIGN KEY (Spouse_CCCD_ID) REFERENCES CITIZEN(CCCD_ID);

-- 14. Add Head_of_Household constraint back
ALTER TABLE CITIZEN
ADD CONSTRAINT fk_citizen_head_of_household FOREIGN KEY (Head_of_Household_CCCD_ID) REFERENCES HOUSEHOLD_BOOK(Head_of_Household_CCCD_ID);

-- --- PART 3: SAMPLE DATA (Logic to safely add Admin) ---

-- 0. Add Administrative Units
INSERT INTO ADMINISTRATIVE_UNIT (Unit_ID, Unit_Name, Address, Unit_Type)
VALUES
('DV001', 'Kim Ma Ward, Ba Dinh, Hanoi', '123 Kim Ma', 'Ward/Commune'),
('DV002', 'Ba Dinh District Police', '456 Giang Vo', 'District');

-- Temporarily disable Head of Household check
ALTER TABLE CITIZEN DROP CONSTRAINT IF EXISTS fk_citizen_head_of_household;

-- 1. Add the Admin to the Citizen table
INSERT INTO CITIZEN (
    CCCD_ID, Full_Name, Date_of_Birth, Gender, Birth_Registration_Place, Place_of_Origin, Ethnicity, Nationality, 
    Permanent_Address, Current_Residence, Relationship_to_Head, Head_of_Household_CCCD_ID, Management_Unit_ID
)
VALUES (
    '000000000001', 'System Admin', '2005-05-05', 'Male', 'Hanoi', 'Hanoi', 'Kinh', 'Vietnam', 
    'Hanoi', 'Hanoi', 'Head of Household', '000000000001', 'DV001'
);

-- 2. Create the Household Book for the Admin
INSERT INTO HOUSEHOLD_BOOK (Household_Book_ID, Head_of_Household_CCCD_ID, Permanent_Residence_Address, Number_of_Members, Issuing_Unit_ID)
VALUES ('HK_ADMIN', '000000000001', 'Hanoi', 1, 'DV001');

-- 3. Update the Citizen with the Household_Book_ID
UPDATE CITIZEN SET Household_Book_ID = 'HK_ADMIN' WHERE CCCD_ID = '000000000001';

-- 4. Create the login account for Admin
INSERT INTO users (username, email, password, full_name, role, cccd_id, Working_Unit_ID) 
VALUES ('admin', 'admin@example.com', 'password_hash', 'Admin User', 'admin', '000000000001', 'DV001');

-- 5. Re-enable the Head of Household check
ALTER TABLE CITIZEN 
ADD CONSTRAINT fk_citizen_head_of_household FOREIGN KEY (Head_of_Household_CCCD_ID) REFERENCES HOUSEHOLD_BOOK(Head_of_Household_CCCD_ID);


-- --- CHECK RESULTS ---
SELECT * FROM users;
SELECT * FROM CITIZEN;
SELECT * FROM HOUSEHOLD_BOOK;
SELECT * FROM ADMINISTRATIVE_UNIT;
