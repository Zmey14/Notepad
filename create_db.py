from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///todo.db?check_same_thread=True')

Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today().date())

    def __repr__(self):
        return self.task

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Menu(Table):
    today = datetime.today()

    def __init__(self):
        self.user = ''

    def choices(self):
        self.user = int(input("\n1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed tasks\n5) Add task\n6) Delete task\n0) Exit\n"))
        if self.user == 1:
            Menu.show_today(self)
        elif self.user == 2: # Вывести задания на всю неделю по дням
            Menu.show_week(self)
        elif self.user == 3: # Вывести все текущие задания
            Menu.show_all(self)
        elif self.user == 4:
            Menu.missed_tasks(self)
        elif self.user == 5:
            Menu.add(self)
        elif self.user == 6:
            Menu.delete(self)
        elif self.user == 0:
            Menu.end(self)

    # Вывод заданий на сегодняшний день
    def show_today(self):
        today = datetime.today().date()
        count = 0

        if session.query(Table).filter(Table.deadline == today).all():
            result = session.query(Table).filter(Table.deadline == today)
            print(f"\nToday {today.strftime('%d %b')}")
            for i in result:
                count += 1
                print(f"{count}. {i}")

        elif session.query(Table).filter(Table.deadline == None):
            print(f"\nToday: {today}:\nNothing to do!")
        return self.choices()

    # Вывод заданий на текущую неделю начиная с сегодняшнего дня плюс 6 дней вперёд
    def show_week(self):
        today = datetime.today()
        week = []

        for i in range(7):
            day = today + timedelta(days=i)
            week.append(day)

        for i in week:
            print("\n" + i.strftime("%A %d %b") + ":")
            rows = session.query(Table).filter(Table.deadline == i.date()).all()
            count = 1
            if not rows:
                print("Nothing to do!")
            elif rows != None:
                for i in rows:
                    print(f"{count}. {i}")
                    count += 1
        return self.choices()

    # Вывод всех заданий
    def show_all(self):
        count = 1
        print()

        for task in session.query(Table).order_by(Table.deadline):
            print(f"{count}. {task}. {task.deadline.strftime('%d %b')}")
            count += 1
        return self.choices()

    # Прошедшие задачи
    def missed_tasks(self):
        print()
        count = 1
        check = session.query(Table).filter(Table.deadline < datetime.today().date())
        if check == None:
            print("Nothing is missed!")
        else:
            tasks = session.query(Table).filter(Table.deadline < datetime.today().date()).order_by(Table.deadline)
            for task in tasks:
                print(f"{count}. {task}. {task.deadline.strftime('%d %b')}")
                count += 1

        return self.choices()

    # Добавление нового задания на определённую дату форматом: 2020-09-30(год, месяц, день)
    def add(self):
        added = input("\nEnter task\n")
        date_input = input("Enter deadline\n")
        new_message = Table(task=added, deadline=datetime.strptime(date_input, "%Y-%m-%d")) # ввод даты
        session.add(new_message)
        session.commit()
        print("The task has been added!\n")
        return self.choices()

    # Удаление задания
    def delete(self):
        count = 1
        task = session.query(Table).filter(Table.deadline)
        for i in task:
            print(f"{count}. {i}. {i.deadline.strftime('%d %b')}")
            count += 1

        print("Choose the number of the task you want to delete:")

        guess = int(input())
        rows = session.query(Table).filter(Table.deadline).all()
        specific_row = rows[guess - 1]
        session.delete(specific_row)
        print("The task has been deleted!\n")
        session.commit()
        return self.choices()

        # else:
        #     print("Nothing to delete")
        #     return self.choices()

    # Выход из прогрммы
    def end(self):
        print("Buy!")
        exit()

menu = Menu()
menu.choices()
