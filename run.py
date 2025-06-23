from student_db import StudentDB

def main():
  
    db = StudentDB('sqlite:///students.db')
    db.load_from_csv('students.csv')
    
    print("1) Студенты факультета 'ФПМИ':")
    students_fpmi = db.get_students_by_faculty('ФПМИ')
    for s in students_fpmi:
        print(s)

    print("\n2) Уникальные курсы:")
    courses = db.get_unique_courses()
    for c in courses:
        print(c)

    print("\n3) Средний балл по факультету 'ФПМИ':")
    avg_score = db.get_avg_score_by_faculty('ФПМИ')
    print(avg_score)

    print("\n4) Студенты по курсу 'Информатика' с оценкой ниже 30:")
    low_score_students = db.get_students_by_course_low_score('Информатика')
    for s in low_score_students:
        print(s)

if __name__ == '__main__':
    main()


