select * from students
INSERT INTO
    students(id,fname,lname,phone)
SELECT setval('students_id_seq', 1, false);