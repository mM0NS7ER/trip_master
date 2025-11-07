import os
import sys
import importlib

# 添加项目路径到sys.path，但要确保不会与已安装的包冲突
project_path = os.path.dirname(os.path.abspath(__file__))
# 先添加app路径，这样我们仍然可以导入自己的模块
sys.path.insert(0, os.path.join(project_path, 'app'))
# 然后添加项目根路径，但放在后面，避免与已安装的包冲突
if project_path not in sys.path:
    sys.path.append(project_path)

def check_python_path():
    """打印Python路径信息用于调试"""
    print("Python路径:")
    for path in sys.path:
        print(f"  - {path}")
    print()

def check_dependencies():
    """检查是否安装了必要的依赖"""
    print("检查依赖包...")
    
    try:
        import alembic
        # 尝试获取版本信息，如果失败则只显示已安装
        try:
            version = alembic.__version__
        except AttributeError:
            version = "未知版本"
        print(f"✓ alembic {version} 已安装")
    except ImportError as e:
        print(f"✗ alembic 未安装: {e}")
        return False
    
    try:
        import sqlalchemy
        # 尝试获取版本信息，如果失败则只显示已安装
        try:
            version = sqlalchemy.__version__
        except AttributeError:
            version = "未知版本"
        print(f"✓ sqlalchemy {version} 已安装")
    except ImportError as e:
        print(f"✗ sqlalchemy 未安装: {e}")
        return False
    
    try:
        import psycopg2
        # 尝试获取版本信息，如果失败则只显示已安装
        try:
            version = psycopg2.__version__
        except AttributeError:
            version = "未知版本"
        print(f"✓ psycopg2 {version} 已安装")
    except ImportError as e:
        print(f"✗ psycopg2-binary 未安装: {e}")
        return False
    
    return True

def init_database():
    """初始化数据库，创建所有表"""
    print("正在初始化数据库...")
    
    # 打印Python路径信息用于调试
    check_python_path()
    
    # 检查依赖
    if not check_dependencies():
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    try:
        # 尝试导入alembic.config
        print("\n正在导入 alembic.config...")
        from alembic.config import Config
        print("✓ 成功导入 alembic.config")
        
        # 尝试导入alembic.command
        print("正在导入 alembic.command...")
        from alembic import command
        print("✓ 成功导入 alembic.command")
        
        # 尝试导入应用配置
        print("正在导入应用配置...")
        from app.core.config import settings
        print("✓ 成功导入应用配置")
        
        # 配置Alembic
        print("正在配置Alembic...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        print("✓ Alembic配置完成")
        
        # 创建迁移（如果不存在）
        print("\n正在创建初始迁移...")
        try:
            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            print("✓ 已创建初始迁移文件")
        except Exception as e:
            print(f"创建迁移文件时出错: {e}")
        
        # 应用迁移
        print("\n正在应用数据库迁移...")
        try:
            command.upgrade(alembic_cfg, "head")
            print("✓ 数据库初始化完成！")
            return True
        except Exception as e:
            print(f"应用迁移时出错: {e}")
            return False
            
    except Exception as e:
        print(f"\n初始化过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)
