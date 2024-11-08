import os
from dotenv import load_dotenv  # Import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, select
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Load environment from variables from .env file 
load_dotenv()

# Database URL from render DONT FORGET postgresql+asyncpg://
DATABASE_URL = f"postgresql://course_python_db_4mil_user:gVdR8SMUZxzmmiLRf1bbHJWdylIy8PdB@dpg-csn1828gph6c73frdbp0-a.oregon-postgres.render.com/course_python_db_4mil"

# Initalization SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocomit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

app = FastAPI()

# Allow origins (for development purposes only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class ItemDB(Base):
    _tablename_ = "items"
    id= Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    price = Column(Float)
    available = Column(Boolean, default=True)

# Create the tables 
@app.on_event('startup')
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_async(Base.metadata.create_all)

# Pydantic models for API Input/Output
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)

# Dependency to get the async session for each request
async def get_db():
    async with SessionLocal() as session: 
        yield session

@app.get('/')
async def root():
    return {"message": "Service is running"}

# GET : Retrieve all items 
@app.get("/items", response_model=List[Item])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await
    items = result.scalars().all()
    return items 

# GET : Retrieve item by ID
@app.get("/items/{item_id}", response_mode=Item)
async def get_item(item_id: int, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemDB).filter(ItemDB.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    return item
