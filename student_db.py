import csv
from sqlalchemy import create_engine, Column, Integer, String, Float, func
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

