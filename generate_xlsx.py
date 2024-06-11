import pandas as pd
from faker import Faker

fake = Faker()

num_students = 5

students_data = []
for _ in range(num_students):
    students_data.append({
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "email": fake.unique.email(),
        "birthday": fake.date_of_birth(minimum_age=18, maximum_age=22).isoformat()
    })

df = pd.DataFrame(students_data)

df.to_excel("students.xlsx", index=False)

print("Excel file 'students.xlsx' created with 5 students.")
