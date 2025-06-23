# Student Database Project

## Описание
Проект реализует хранение и работу с данными студентов, полученными из CSV-файла `students.csv`.

Используется SQLAlchemy для модели данных и управления БД SQLite.

## Функционал
- Модель данных для таблицы студентов
- Класс `StudentDB` с методами:
  - добавление данных из CSV
  - получение студентов по факультету
  - получение списка уникальных курсов
  - получение среднего балла по факультету
  - получение студентов по курсу с оценкой ниже 30

## Запуск
1. Убедитесь, что установлен SQLAlchemy:
   ```
   pip install sqlalchemy
   ```
2. Импортируйте класс из `student_db.py` и используйте методы.

## Пример использования

```python
from student_db import StudentDB

db = StudentDB('sqlite:///students.db')
db.load_from_csv('students.csv')

students_avtf = db.get_students_by_faculty('АВТФ')
unique_courses = db.get_unique_courses()
avg_score_fpm = db.get_avg_score_by_faculty('ФПМИ')
low_score_students = db.get_students_by_course_low_score('Информатика', 30)
```
