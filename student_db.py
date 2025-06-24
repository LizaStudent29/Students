import csv
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    faculty = Column(String, nullable=False)
    course = Column(String, nullable=False)
    score = Column(Integer, nullable=False)

    def __repr__(self):
        return (f"{self.last_name} {self.first_name} | "
                f"Факультет: {self.faculty} | Курс: {self.course} | Балл: {self.score}")

class StudentDB:
    def __init__(self, db_url='sqlite:///students.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def load_from_csv(self, csv_path):
        session = self.Session()
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student(
                    last_name=row['Фамилия'],
                    first_name=row['Имя'],
                    faculty=row['Факультет'],
                    course=row['Курс'],
                    score=int(row['Оценка'])
                )
                session.add(student)
            session.commit()
        session.close()

    def get_all_students(self):
        """Получить всех студентов"""
        session = self.Session()
        students = session.query(Student).all()
        session.close()
        return students

    def insert_student(self, last_name, first_name, faculty, course, score):
        """Добавить нового студента"""
        session = self.Session()
        student = Student(
            last_name=last_name,
            first_name=first_name,
            faculty=faculty,
            course=course,
            score=score
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        session.close()
        return student

    def get_students_by_faculty(self, faculty_name):
        session = self.Session()
        results = session.query(Student).filter(Student.faculty == faculty_name).all()
        session.close()
        return results

    def get_unique_courses(self):
        session = self.Session()
        courses = session.query(Student.course).distinct().all()
        session.close()
        return [c[0] for c in courses]

    def get_avg_score_by_faculty(self, faculty_name):
        session = self.Session()
        avg_score = session.query(func.avg(Student.score)).filter(Student.faculty == faculty_name).scalar()
        session.close()
        if avg_score is None:
            return 0
        return round(avg_score, 2)

    def get_students_by_course_low_score(self, course_name, threshold=30):
        session = self.Session()
        results = session.query(Student).filter(Student.course == course_name, Student.score < threshold).all()
        session.close()
        return results

    def update_student(self, student_id, **kwargs):
        """Обновить данные студента по его ID"""
        session = self.Session()
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            session.close()
            return None
        for key, value in kwargs.items():
            if hasattr(student, key) and value is not None:
                setattr(student, key, value)
        session.commit()
        session.refresh(student)
        session.close()
        return student

    def delete_student_by_id(self, student_id):
        """Удалить студента по ID"""
        session = self.Session()
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            session.close()
            return False
        session.delete(student)
        session.commit()
        session.close()
        return True
