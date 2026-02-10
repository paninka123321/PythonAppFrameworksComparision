from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # <--- WAŻNE: To pozwala na logowanie sesyjne

db = SQLAlchemy()

# --- TABELE ŁĄCZĄCE (ASSOCIATION TABLES) ---

# 1. Tabela łącząca Użytkowników z Rolami (Wiele-do-Wielu)
# Użytkownik może mieć wiele ról (np. Manager + HR), a rola wielu użytkowników.
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# 2. Tabela łącząca Zadania z Użytkownikami (Wiele-do-Wielu)
# Jedno zadanie może robić wiele osób, jedna osoba ma wiele zadań.
task_assignments = db.Table('task_assignments',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True)
)

# --- MODELE ---

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True) # np. "Manager", "Pracownik"
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(UserMixin, db.Model): # <--- Dziedziczenie po UserMixin jest kluczowe!
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(200)) 
    
    # Relacja do ról (przez tabelę user_roles)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    # Funkcja pomocnicza do sprawdzania uprawnień w kodzie (np. w app.py)
    def has_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return True
        return False

    def __str__(self):
        return self.username

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    
    # Nowość: Status do tablicy Kanban (not_started, in_process, done)
    status = db.Column(db.String(20), default='not_started')

    # Relacja do użytkowników
    assigned_to = db.relationship('User', secondary=task_assignments, backref=db.backref('tasks', lazy=True))

    def __str__(self):
        return self.title

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    year = db.Column(db.Integer) # Pomocnicze pole do szybkiego filtrowania po roku
    description = db.Column(db.String(200), nullable=True)

    def __str__(self):
        return f"{self.category} - {self.date}"

class BusinessDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.Text, nullable=False)

    def __str__(self):
        return self.term

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"