from typing import Optional
from fastapi import FastAPI, Depends
from .schemes import DeviceStat, Statistic, User
from .database import get_db, SessionLocal, Base, engine
from .tasks.analysis import analysis

app = FastAPI()

Base.metadata.create_all(bind=engine)


# сбор статистики с устройства
@app.post("/stats/{device_id}")
def create_stat(device_id: str, user_id: int, stat: Statistic, db: SessionLocal = Depends(get_db)):
    db_stat = DeviceStat(device_id=device_id, user_id=user_id, **stat.dict())
    db.add(db_stat)
    db.commit()
    return {"message": "Stat created successfully"}


# создание нового пользователя
@app.post("/users/")
def create_user(username: str, email: str, password: str, db: SessionLocal = Depends(get_db)):
    db_user = User(username=username, email=email)
    db_user.create_password_hash(password)
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}


# анализ собранной статистики за определенный период
@app.get("/stats/{device_id}/summary", summary="date example:2008-09-15T15:53:00+05:00")
def get_stat_summary(device_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    task_result = analysis.delay(device_id, None, start_date, end_date)
    result = task_result.get()[0][0]
    if result['count_x'] != 0:
        return {
            "x": {
                "min_value": result['min_x'],
                "max_value": result['max_x'],
                "count": result['count_x'],
                "sum": result['sum_x'],
                "median": result['median_x']
            },
            "y": {
                "min_value": result['min_y'],
                "max_value": result['max_y'],
                "count": result['count_y'],
                "sum": result['sum_y'],
                "median": result['median_y']
            },
            "z": {
                "min_value": result['min_z'],
                "max_value": result['max_z'],
                "count": result['count_z'],
                "sum": result['sum_z'],
                "median": result['median_z']
            }
        }
    else:
        return {"message": "No stats found"}


# Метод для получения агрегированных результатов для всех устройств пользователя
@app.get("/users/{user_id}/stats/summary")
def get_user_stats_summary(user_id: int):
    task_result = analysis.delay(None, user_id, None, None)
    result = task_result.get()[0][0]
    if result['count_x'] != 0:
        return {
            "x": {
                "min_value": result['min_x'],
                "max_value": result['max_x'],
                "count": result['count_x'],
                "sum": result['sum_x'],
                "median": result['median_x']
            },
            "y": {
                "min_value": result['min_y'],
                "max_value": result['max_y'],
                "count": result['count_y'],
                "sum": result['sum_y'],
                "median": result['median_y']
            },
            "z": {
                "min_value": result['min_z'],
                "max_value": result['max_z'],
                "count": result['count_z'],
                "sum": result['sum_z'],
                "median": result['median_z']
            }
        }
    else:
        return {"message": "No stats found"}


# Метод для получения агрегированных результатов для каждого устройства пользователя отдельно
@app.get("/users/{user_id}/devices/{device_id}/stats/summary")
def get_user_device_stats_summary(user_id: int, device_id: str):
    task_result = analysis.delay(device_id, user_id, None, None)
    result = task_result.get()[0][0]
    if result['count_x'] != 0:
        return {
            "x": {
                "min_value": result['min_x'],
                "max_value": result['max_x'],
                "count": result['count_x'],
                "sum": result['sum_x'],
                "median": result['median_x']
            },
            "y": {
                "min_value": result['min_y'],
                "max_value": result['max_y'],
                "count": result['count_y'],
                "sum": result['sum_y'],
                "median": result['median_y']
            },
            "z": {
                "min_value": result['min_z'],
                "max_value": result['max_z'],
                "count": result['count_z'],
                "sum": result['sum_z'],
                "median": result['median_z']
            }
        }
    else:
        return {"message": "No stats found"}
