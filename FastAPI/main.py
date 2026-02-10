import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, selectinload
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Table, Float, select
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- CONFIGURATION ---
DATABASE_URL = "sqlite+aiosqlite:///./projekt_firmowy.db"
SECRET_KEY = "twoj-sekretny-klucz-zmien-go"
ALGORITHM = "HS256"

# --- DATABASE SETUP ---
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- MODELS ---
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

task_assignments = Table(
    'task_assignments', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    def __str__(self): return self.name

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    roles = relationship("Role", secondary=user_roles, backref="users", lazy="selectin")
    tasks = relationship("Task", secondary=task_assignments, back_populates="assigned_to", lazy="selectin")
    
    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)
    def __str__(self): return self.username

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    due_date = Column(Date, nullable=True)
    status = Column(String, default="not_started")
    assigned_to = relationship("User", secondary=task_assignments, back_populates="tasks", lazy="selectin")
    def __str__(self): return self.title

class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    date = Column(Date)
    description = Column(String, nullable=True)

class BusinessDefinition(Base):
    __tablename__ = "definitions"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String)
    definition = Column(Text)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)

# --- AUTH UTILS ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(select(User).where(User.username == username).options(selectinload(User.roles)))
    user = result.scalars().first()
    if user is None: raise HTTPException(status_code=401, detail="User not found")
    return user

# --- APP SETUP ---
app = FastAPI(title="Projekt Firmowy API")

# Serve simple frontend templates and static files for presentation
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 1. MIDDLEWARE SESJI (Wymagane do logowania w Adminie)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOGIKA ADMINA (Auth + Widoki) ---

# Backend logowania
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username).options(selectinload(User.roles)))
            user = result.scalars().first()

        # Wpuszczamy KAŻDEGO z dobrym hasłem, ale oznaczamy czy jest Managerem
        if user and verify_password(password, user.hashed_password):
            request.session.update({
                "token": user.username,
                "is_manager": user.has_role("Manager") # Zapisujemy uprawnienia w sesji
            })
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") is not None

# Klasa bazowa dla widoków Szefa (wymaga flagi is_manager)
class ManagerView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return request.session.get("token") is not None and request.session.get("is_manager") is True

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)

# Klasa bazowa dla widoków Pracownika (wymaga tylko logowania)
class EmployeeView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return request.session.get("token") is not None

    def is_visible(self, request: Request) -> bool:
        return self.is_accessible(request)

# Konfiguracja Widoków
class UserAdmin(ManagerView, model=User): # Tylko Manager
    column_list = [User.id, User.username, User.roles]
    icon = "fa-solid fa-user"

class RoleAdmin(ManagerView, model=Role): # Tylko Manager
    column_list = [Role.name, Role.description]
    icon = "fa-solid fa-shield-halved"

class TaskAdmin(EmployeeView, model=Task): # Każdy
    column_list = [Task.title, Task.status]
    form_columns = [Task.title, Task.description, Task.status, Task.due_date, Task.assigned_to]
    icon = "fa-solid fa-list-check"

class BillAdmin(EmployeeView, model=Bill): # Każdy
    column_list = [Bill.category, Bill.amount, Bill.date]
    icon = "fa-solid fa-money-bill"

class DefAdmin(EmployeeView, model=BusinessDefinition): # Każdy
    column_list = [BusinessDefinition.term]
    icon = "fa-solid fa-book"

class EmpAdmin(EmployeeView, model=Employee): # Każdy
    column_list = [Employee.last_name, Employee.email]
    icon = "fa-solid fa-users"

# Inicjalizacja Admina
authentication_backend = AdminAuth(secret_key=SECRET_KEY)
admin = Admin(app, engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(RoleAdmin)
admin.add_view(TaskAdmin)
admin.add_view(BillAdmin)
admin.add_view(DefAdmin)
admin.add_view(EmpAdmin)

# --- SCHEMAS ---
class RoleSchema(BaseModel):
    name: str
    class Config: from_attributes = True

class UserRead(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[RoleSchema] = []
    is_admin: bool = False 
    class Config: from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: Optional[date] = None
    status: str = "not_started"
    assigned_to_ids: List[int] = [] 

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    assigned_to_ids: Optional[List[int]] = None

class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    due_date: Optional[date] = None
    status: str
    assigned_to: List[UserRead] = []
    class Config: from_attributes = True

class BillSchema(BaseModel):
    id: int
    category: str
    amount: float
    date: date
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- ROUTES ---
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me/", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    user_response = UserRead.model_validate(current_user)
    user_response.is_admin = current_user.has_role("Manager")
    return user_response

@app.get("/api/users/", response_model=List[UserRead])
async def get_all_users(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@app.get("/api/tasks/", response_model=List[TaskRead])
async def get_tasks(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).options(selectinload(Task.assigned_to)))
    return result.scalars().all()

@app.post("/api/tasks/", response_model=TaskRead)
async def create_task(task_in: TaskCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task_in.title, description=task_in.description, due_date=task_in.due_date, status=task_in.status)
    if task_in.assigned_to_ids:
        if not current_user.has_role("Manager"):
             raise HTTPException(status_code=403, detail="Only Managers can assign users.")
        result = await db.execute(select(User).where(User.id.in_(task_in.assigned_to_ids)))
        users = result.scalars().all()
        new_task.assigned_to = users
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    result = await db.execute(select(Task).where(Task.id == new_task.id).options(selectinload(Task.assigned_to)))
    return result.scalars().first()

@app.patch("/api/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_in: TaskUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id).options(selectinload(Task.assigned_to)))
    task = result.scalars().first()
    if not task: raise HTTPException(status_code=404, detail="Task not found")

    if task_in.title is not None: task.title = task_in.title
    if task_in.description is not None: task.description = task_in.description
    if task_in.due_date is not None: task.due_date = task_in.due_date
    if task_in.status is not None: task.status = task_in.status 

    if task_in.assigned_to_ids is not None:
        if not current_user.has_role("Manager"):
             raise HTTPException(status_code=403, detail="Only Managers can assign users.")
        user_result = await db.execute(select(User).where(User.id.in_(task_in.assigned_to_ids)))
        users = user_result.scalars().all()
        task.assigned_to = users

    await db.commit()
    await db.refresh(task)
    return task

@app.get("/api/bills/", response_model=List[BillSchema])
async def get_bills(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bill).where(Bill.date >= date(2025, 1, 1), Bill.date <= date(2026, 12, 31)))
    return result.scalars().all()


# --- SIMPLE HTML PANEL FOR PRESENTATION ---
@app.get("/staff/tasks/", response_class=HTMLResponse)
async def users_tasks_view(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).options(selectinload(User.tasks)))
    users = result.scalars().all()
    return templates.TemplateResponse("users_tasks.html", {"request": request, "users": users})

# --- STARTUP LOGIC ---
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # 1. Create Role Manager
        result = await session.execute(select(Role).where(Role.name == "Manager"))
        manager_role = result.scalars().first()
        if not manager_role:
            print("--- Creating Manager Role ---")
            manager_role = Role(name="Manager", description="Full Access")
            session.add(manager_role)
            await session.commit()

        # 2. Create Admin (Manager)
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalars().first()
        if not existing_admin:
            print("--- Creating admin user ---")
            hashed = get_password_hash("adminpassword")
            admin_user = User(username="admin", hashed_password=hashed, first_name="Admin", last_name="System")
            admin_user.roles.append(manager_role)
            session.add(admin_user)
            await session.commit()
            print("--- Admin created ---")
        
        # 3. Create Adam (Employee)
        result = await session.execute(select(User).where(User.username == "adam"))
        if not result.scalars().first():
            print("--- Creating user adam ---")
            hashed = get_password_hash("password")
            adam = User(username="adam", hashed_password=hashed, first_name="Adam", last_name="Worker")
            session.add(adam)
            await session.commit()
            print("--- User Adam created ---")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)