from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from supabase import create_client, Client

# 创建Supabase客户端（仅在配置存在时）
supabase: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        print(f"初始化Supabase客户端: {settings.SUPABASE_URL}")
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("Supabase客户端初始化成功")
    except Exception as e:
        print(f"创建Supabase客户端失败: {str(e)}")
        supabase = None

# 保留SQLAlchemy引擎和会话
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖函数：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 新增：获取Supabase客户端
def get_supabase():
    if supabase is None:
        raise Exception("Supabase客户端未初始化，请检查配置")
    return supabase
