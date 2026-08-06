from fastapi import FastAPI

from .routers.charts import downloads_router

app = FastAPI()
app.include_router(downloads_router)
