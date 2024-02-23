from statistics import median
from app.schemes import DeviceStat
from sqlalchemy.sql import func
from app.database import SessionLocal
from app.celery_app import app
from celery.result import AsyncResult


@app.task(trail=True)
def analysis(device_id, user_id, start_date, end_date):
    db = SessionLocal()
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
    if device_id:
        query = query.filter(DeviceStat.device_id == device_id)
        query1 = query1.filter(DeviceStat.device_id == device_id)
        query2 = query2.filter(DeviceStat.device_id == device_id)
        query3 = query3.filter(DeviceStat.device_id == device_id)
    if user_id:
        query = query.filter(DeviceStat.user_id == user_id)
        query1 = query1.filter(DeviceStat.user_id == user_id)
        query2 = query2.filter(DeviceStat.user_id == user_id)
        query3 = query3.filter(DeviceStat.user_id == user_id)
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
    if result.count_x != 0:
        median_x = median(list([x[0] for x in query1.all()]))
        median_y = median(list([y[0] for y in query2.all()]))
        median_z = median(list([z[0] for z in query3.all()]))
    else:
        median_x = None
        median_y = None
        median_z = None
    if result:
        res = {col: getattr(result, col) for col in result._fields}
        result = res.update({'median_x': median_x, 'median_y': median_y, 'median_z': median_z})
        return AsyncResult(res)
