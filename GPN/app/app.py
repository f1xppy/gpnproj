from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import datetime
from statistics import median

app = FastAPI()


class Config(BaseSettings):
    mysql_user: str = Field(
        default='gpn',
        env='MYSQL_USER',
        alias='MYSQL_USER'
    )

    mysql_host: str = Field(
        default='localhost',
        env='MYSQL_HOST',
        alias='MYSQL_HOST'
    )

    mysql_password: str = Field(
        default='gpnpa$$Word',
        env='MYSQL_PASSWORD',
        alias='MYSQL_PASSWORD'
    )

    mysql_database: str = Field(
        default='gpn',
        env='MYSQL_DATABASE',
        alias='MYSQL_DATABASE'
    )

    class Config:
        env_file = ".env"


def load_config():
    return Config()


cfg: Config = load_config()


# Инициализация базы данных
SQLALCHEMY_DATABASE_URL = f"mysql+mysqldb://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}/{cfg.mysql_database}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение модели данных для статистики устройства
class DeviceStat(Base):
    __tablename__ = "device_stats"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), index=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)


class Statistic(BaseModel):
    x: float
    y: float
    z: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# сбор статистики с устройства
@app.post("/stats/{device_id}")
def create_stat(device_id: str, stat: Statistic, db: SessionLocal = Depends(get_db)):
    db_stat = DeviceStat(device_id=device_id, **stat.dict())
    db.add(db_stat)
    db.commit()
    return {"message": "Stat created successfully"}


# анализ собранной статистики за определенный период
@app.get("/stats/{device_id}/summary")
def get_stat_summary(device_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None,
                     db: SessionLocal = Depends(get_db)):
    query = (
        db.query(
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
        .filter(DeviceStat.device_id == device_id)
    )
    query1 = (db.query(DeviceStat.x)).filter(DeviceStat.device_id == device_id)
    query2 = (db.query(DeviceStat.y)).filter(DeviceStat.device_id == device_id)
    query3 = (db.query(DeviceStat.z)).filter(DeviceStat.device_id == device_id)
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

    result = query.first()

    if result.count_x != 0 or result.count_y != 0 or result.count_z != 0:
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
        return {"message": "No stats found for the specified device or period"}
