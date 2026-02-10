from flask import Flask, jsonify, request, session, redirect, url_for, render_template_string
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink # <--- Ważne do przycisku Wyloguj
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# Importy modeli i schematów
from models import db, User, Task, BusinessDefinition, Employee, Bill, Role
from serializers import ma, TaskSchema, BillSchema, UserSchema, BusinessDefinitionSchema

app = Flask(__name__)

# --- KONFIGURACJA ---
app.config['SECRET_KEY'] = 'twoj-sekretny-klucz-sesji' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projekt_firmowy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-sekretny-klucz'

db.init_app(app)
ma.init_app(app)
jwt = JWTManager(app)
CORS(app)

# --- KONFIGURACJA FLASK-LOGIN (Dla Panelu Admina) ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- SCHEMATY (Marshmallow) ---
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
bill_schema = BillSchema()
bills_schema = BillSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
def_schema = BusinessDefinitionSchema(many=True)

# --- CUSTOMOWE WIDOKI ADMINA ---

# 1. Widok "Tylko dla Szefa" (User, Role)
class SuperAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('Manager')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# 2. Widok "Dla Pracowników" (Tasks, Bills)
class GeneralView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# 3. Widok Dashboardu (Strona główna panelu)
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_login'))
        return super(MyAdminIndexView, self).index()

# --- REJESTRACJA ADMINA ---
admin = Admin(app, name='Panel Firmowy', index_view=MyAdminIndexView())

# Widoki
admin.add_view(SuperAdminView(User, db.session, name="Użytkownicy (Szef)"))
admin.add_view(SuperAdminView(Role, db.session, name="Uprawnienia (Szef)"))
admin.add_view(GeneralView(Task, db.session, name="Zadania"))
admin.add_view(GeneralView(Bill, db.session, name="Rachunki"))
admin.add_view(GeneralView(Employee, db.session, name="Pracownicy"))
admin.add_view(GeneralView(BusinessDefinition, db.session, name="Słownik"))

# Przycisk Wyloguj w menu
admin.add_link(MenuLink(name='Wyloguj', category='', url='/admin-logout'))

# --- TRASY LOGOWANIA DO ADMINA (HTML) ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # UWAGA: W produkcji używaj hashów haseł!
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('admin.index'))
            
        return "Błędny login lub hasło"
    
    return render_template_string('''
        <div style="display:flex; justify-content:center; align-items:center; height:100vh; background:#f4f4f4;">
            <form method="POST" style="background:white; padding:20px; border-radius:8px; box-shadow:0 0 10px rgba(0,0,0,0.1);">
                <h3 style="margin-top:0;">Panel Firmowy</h3>
                <input type="text" name="username" placeholder="Login" style="display:block; margin:10px 0; padding:5px; width:200px;">
                <input type="password" name="password" placeholder="Hasło" style="display:block; margin:10px 0; padding:5px; width:200px;">
                <input type="submit" value="Zaloguj" style="width:100%; padding:5px; cursor:pointer;">
            </form>
        </div>
    ''')

@app.route('/admin-logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# --- API ENDPOINTS (DLA REACTA) ---

# 1. Login (JWT)
@app.route('/api/token/', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"msg": "Błędny login lub hasło"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

# 2. Current User
@app.route('/api/me/', methods=['GET'])
@jwt_required()
def get_me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    # Serializer UserSchema sam obliczy pole 'is_admin'
    return user_schema.dump(user)

# 3. Lista userów (dla dropdownu)
@app.route('/api/users/', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

# 4. Tasks (GET / POST)
@app.route('/api/tasks/', methods=['GET', 'POST'])
@jwt_required()
def handle_tasks():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if request.method == 'GET':
        tasks = Task.query.all()
        return jsonify(tasks_schema.dump(tasks))
    
    if request.method == 'POST':
        data = request.json
        due_date_val = None
        if data.get('due_date'):
            try:
                due_date_val = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
            except ValueError:
                pass

        new_task = Task(
            title=data.get('title'),
            description=data.get('description'),
            due_date=due_date_val,
            status='not_started'
        )
        
        # Przypisywanie ludzi (tylko Manager)
        user_ids = data.get('assigned_to_ids', [])
        if user_ids:
            if not current_user.has_role('Manager'):
                 return jsonify({"msg": "Brak uprawnień. Tylko Manager."}), 403
            users = User.query.filter(User.id.in_(user_ids)).all()
            new_task.assigned_to.extend(users)
            
        db.session.add(new_task)
        db.session.commit()
        return task_schema.dump(new_task), 201

# 5. Task Update (PATCH)
@app.route('/api/tasks/<int:task_id>/', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    task = Task.query.get_or_404(task_id)
    data = request.json

    # Zmiana statusu (każdy może)
    if 'status' in data:
        task.status = data['status']

    # Zmiana osób (tylko Manager)
    if 'assigned_to_ids' in data:
        if not current_user.has_role('Manager'):
            return jsonify({"msg": "Brak uprawnień. Tylko Manager."}), 403
        
        user_ids = data['assigned_to_ids']
        users = User.query.filter(User.id.in_(user_ids)).all()
        task.assigned_to = users 

    db.session.commit()
    return task_schema.dump(task)

# 6. Rachunki (z obsługą year)
@app.route('/api/bills/', methods=['GET'])
# @jwt_required()
def get_bills():
    # Pobieramy wszystko z 2025 i 2026
    bills = Bill.query.filter(
        Bill.date >= '2025-01-01',
        Bill.date <= '2026-12-31'
    ).all()
    return jsonify(bills_schema.dump(bills))

# 7. Słownik
@app.route('/api/definitions/', methods=['GET'])
@jwt_required()
def get_definitions():
    defs = BusinessDefinition.query.all()
    return jsonify(def_schema.dump(defs))


# --- START APLIKACJI I DANE POCZĄTKOWE ---
if __name__ == '__main__':
    with app.app_context():
        # 1. Tworzenie tabel
        db.create_all()
        
        # 2. Tworzenie Roli Manager
        if not Role.query.filter_by(name='Manager').first():
            print("--- Tworzę rolę Manager... ---")
            manager_role = Role(name='Manager', description="Pełny dostęp")
            db.session.add(manager_role)
            db.session.commit()

        # 3. Tworzenie Admina (Szefa)
        if not User.query.filter_by(username='admin').first():
            print("--- Tworzę usera admin... ---")
            admin_user = User(
                username='admin', 
                password='adminpassword', 
                first_name="Szef", 
                last_name="Systemu"
            )
            # Daj role Managera
            role = Role.query.filter_by(name='Manager').first()
            admin_user.roles.append(role)
            db.session.add(admin_user)
            db.session.commit()

        # 4. Tworzenie Adama (Pracownika)
        if not User.query.filter_by(username='adam').first():
            print("--- Tworzę usera adam... ---")
            adam = User(
                username='adam', 
                password='password', 
                first_name="Adam", 
                last_name="Kowalski"
            )
            # Adam NIE dostaje roli Manager
            db.session.add(adam)
            db.session.commit()

        # 5. Tworzenie Rachunków (Dla Wykresów React)
        if not Bill.query.first():
            print("--- Generowanie rachunków... ---")
            sample_bills = [
                # 2025
                Bill(category="Prąd", amount=150.0, date=datetime(2025,1,10).date(), year=2025),
                Bill(category="Prąd", amount=160.0, date=datetime(2025,2,10).date(), year=2025),
                Bill(category="Internet", amount=60.0, date=datetime(2025,1,5).date(), year=2025),
                Bill(category="Biuro", amount=1000.0, date=datetime(2025,1,1).date(), year=2025),
                # 2026
                Bill(category="Prąd", amount=250.0, date=datetime(2026,1,10).date(), year=2026),
                Bill(category="Prąd", amount=260.0, date=datetime(2026,2,10).date(), year=2026),
                Bill(category="Internet", amount=70.0, date=datetime(2026,1,5).date(), year=2026),
                Bill(category="Biuro", amount=1100.0, date=datetime(2026,1,1).date(), year=2026),
            ]
            for b in sample_bills: db.session.add(b)
            db.session.commit()
            print("--- Rachunki dodane! ---")

    app.run(debug=True, port=8003)