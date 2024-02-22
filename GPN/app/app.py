from typing import Optional
from fastapi import FastAPI, Depends
from sqlalchemy.sql import func
from statistics import median
from .schemes import DeviceStat, Statistic, User
from .database import get_db, SessionLocal, Base, engine

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


def get_queries(db):
    query1 = (db.query(DeviceStat.x))
    query2 = (db.query(DeviceStat.y))
    query3 = (db.query(DeviceStat.z))
    query = db.query(
            func.min(DeviceStat.x).label("min_x"),
            func.max(DeviceStat.x).label("max_x"),
            func.count(DeviceStat.x).label("count_x"),
            func.sum(DeviceStat.x).label("sum_x"),
            func.min(DeviceStat.y).label("min_y"),
            func.max(DeviceStat.y).label("max_y"),
            func.count(DeviceStat.y).label("count_y"),
            func.sum(DeviceStat.y).label("sum_y"),
            func.min(DeviceStat.z).label("min_z"),
            func.max(DeviceStat.z).label("max_z"),
            func.count(DeviceStat.z).label("count_z"),
            func.sum(DeviceStat.z).label("sum_z"),
        )
    return [query, query1, query2, query3]


def analysis(query, query1, query2, query3):
    result = query.first()

    if result.count_x != 0:
        if result.count_x != 0:
            median_x = median([x[0] for x in query1.all()])
        else:
            median_x = None
        if result.count_y != 0:
            median_y = median([y[0] for y in query2.all()])
        else:
            median_y = None
        if result.count_z != 0:
            median_z = median([z[0] for z in query3.all()])
        else:
            median_z = None
        return {
            "x": {
                "min_value": result.min_x,
                "max_value": result.max_x,
                "count": result.count_x,
                "sum": result.sum_x,
                "median": median_x
            },
            "y": {
                "min_value": result.min_y,
                "max_value": result.max_y,
                "count": result.count_y,
                "sum": result.sum_y,
                "median": median_y
            },
            "z": {
                "min_value": result.min_z,
                "max_value": result.max_z,
                "count": result.count_z,
                "sum": result.sum_z,
                "median": median_z
            }
        }
    else:
        return {"message": "No stats found"}


# анализ собранной статистики за определенный период
@app.get("/stats/{device_id}/summary")
def get_stat_summary(device_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None,
                     db: SessionLocal = Depends(get_db)):

    q = get_queries(db)
    query = q[0].filter(DeviceStat.device_id == device_id)
    query1 = q[1].filter(DeviceStat.device_id == device_id)
    query2 = q[2].filter(DeviceStat.device_id == device_id)
    query3 = q[3].filter(DeviceStat.device_id == device_id)

    if start_date:
        query = query.filter(DeviceStat.created_at >= start_date)
        query1 = query1.filter(DeviceStat.created_at >= start_date)
        query2 = query2.filter(DeviceStat.created_at >= start_date)
        query3 = query3.filter(DeviceStat.created_at >= start_date)
    if end_date:
        query = query.filter(DeviceStat.created_at <= end_date)
        query1 = query1.filter(DeviceStat.created_at <= end_date)
        query2 = query2.filter(DeviceStat.created_at <= end_date)
        query3 = query3.filter(DeviceStat.created_at <= end_date)

    return analysis(query, query1, query2, query3)


# Метод для получения агрегированных результатов для всех устройств пользователя
@app.get("/users/{user_id}/stats/summary")
def get_user_stats_summary(user_id: int, db: SessionLocal = Depends(get_db)):
    q = get_queries(db)
    query = q[0].filter(DeviceStat.user_id == user_id)
    query1 = q[1].filter(DeviceStat.user_id == user_id)
    query2 = q[2].filter(DeviceStat.user_id == user_id)
    query3 = q[3].filter(DeviceStat.user_id == user_id)

    return analysis(query, query1, query2, query3)


# Метод для получения агрегированных результатов для каждого устройства пользователя отдельно
@app.get("/users/{user_id}/devices/{device_id}/stats/summary")
def get_user_device_stats_summary(user_id: int, device_id: str, db: SessionLocal = Depends(get_db)):
    q = get_queries(db)
    query = q[0].filter(DeviceStat.user_id == user_id).filter(DeviceStat.device_id == device_id)
    query1 = q[1].filter(DeviceStat.user_id == user_id).filter(DeviceStat.device_id == device_id)
    query2 = q[2].filter(DeviceStat.user_id == user_id).filter(DeviceStat.device_id == device_id)
    query3 = q[3].filter(DeviceStat.user_id == user_id).filter(DeviceStat.device_id == device_id)

    return analysis(query, query1, query2, query3)
