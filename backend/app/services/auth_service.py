from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from supabase import Client

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.database import get_supabase
from ..core.config import settings


class AuthService:
    """认证服务类，整合Supabase Auth功能"""
    
    def __init__(self):
        try:
            self.supabase: Client = get_supabase()
        except Exception as e:
            print(f"Supabase客户端不可用: {str(e)}")
            self.supabase = None
    
    def _check_supabase(self):
        """检查Supabase客户端是否可用"""
        if self.supabase is None:
            raise Exception("Supabase客户端不可用，请检查配置")
    
    def sign_up(self, email: str, password: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用Supabase Auth注册用户"""
        self._check_supabase()
            
        try:
            # 在Supabase中创建用户
            print(f"尝试注册用户: {email}")
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data,
                    "email_confirm": True  # 禁用邮箱验证要求
                }
            })
            print(f"注册响应: {response}")
            
            if response.user:
                # 用户创建成功，返回用户信息和会话
                return {
                    "user": response.user,
                    "session": response.session
                }
            else:
                raise Exception("用户创建失败")
        except Exception as e:
            raise Exception(f"注册失败: {str(e)}")
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """使用Supabase Auth登录用户"""
        self._check_supabase()
        try:
            # 使用Supabase进行身份验证
            print(f"尝试登录用户: {email}")
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            print(f"登录响应: {response}")
            
            if response.user:
                # 登录成功，返回用户信息和会话
                print(f"用户 {email} 登录成功")
                return {
                    "user": response.user,
                    "session": response.session
                }
            else:
                raise Exception("登录失败")
        except Exception as e:
            # 提供更详细的错误信息
            error_message = str(e)
            print(f"登录失败详情: {error_message}")

            # 根据错误类型提供更具体的错误信息
            if "Invalid login credentials" in error_message:
                raise Exception("登录失败：邮箱或密码不正确")
            elif "Email not confirmed" in error_message:
                raise Exception("登录失败：邮箱尚未验证，请检查您的邮箱并点击验证链接")
            elif "User not found" in error_message:
                raise Exception("登录失败：用户不存在，请先注册")
            else:
                raise Exception(f"登录失败: {error_message}")
    
    def sign_out(self, access_token: str) -> bool:
        """使用Supabase Auth登出用户"""
        self._check_supabase()
        try:
            # 设置认证令牌
            # 对于新版本的Supabase，set_session需要两个参数：access_token和refresh_token
            self.supabase.auth.set_session(access_token, "")
            
            # 登出用户
            response = self.supabase.auth.sign_out()
            return True
        except Exception as e:
            raise Exception(f"登出失败: {str(e)}")
    
    def get_current_user(self, access_token: str, refresh_token: str = None) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        self._check_supabase()
        try:
            # 设置认证令牌
            # 对于新版本的Supabase，set_session需要两个参数：access_token和refresh_token
            # 如果没有refresh_token，可以传入空字符串
            self.supabase.auth.set_session(access_token, refresh_token or "")
            
            # 获取当前用户
            # 传入access_token作为参数
            response = self.supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            return None
        except Exception as e:
            raise Exception(f"获取用户信息失败: {str(e)}")
    
    def update_user(self, access_token: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        self._check_supabase()
        try:
            # 设置认证令牌
            # 对于新版本的Supabase，set_session需要两个参数：access_token和refresh_token
            self.supabase.auth.set_session(access_token, "")
            
            # 更新用户信息
            response = self.supabase.auth.update_user(user_data)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            return None
        except Exception as e:
            raise Exception(f"更新用户信息失败: {str(e)}")
    
    def reset_password(self, email: str) -> bool:
        """发送密码重置邮件"""
        self._check_supabase()
        try:
            # 发送密码重置邮件
            response = self.supabase.auth.reset_password_for_email(email)
            return True
        except Exception as e:
            raise Exception(f"发送密码重置邮件失败: {str(e)}")
    
    def create_guest_user(self, db: Session) -> User:
        """创建访客用户（保留原有实现，不使用Supabase）"""
        # 生成唯一的访客用户名
        import uuid
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"

        db_user = User(
            email="guest@example.com",
            username=guest_username,
            name="访客用户",
            hashed_password=None,  # 访客用户没有密码
            is_active=True,
            is_verified=False,
            is_guest=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def sync_supabase_user_to_db(self, db: Session, supabase_user_id: str, email: str, user_data: Dict[str, Any]) -> User:
        """将Supabase用户同步到本地数据库"""
        # 检查用户是否已存在于本地数据库
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # 创建新用户
            user = User(
                id=UUID(supabase_user_id),  # 使用Supabase用户ID
                email=email,
                username=user_data.get("username", email.split("@")[0]),
                name=user_data.get("name", "用户"),
                hashed_password=None,  # 密码由Supabase管理
                age=user_data.get("age"),
                bio=user_data.get("bio"),
                avatar_url=user_data.get("avatar_url"),
                is_active=True,
                is_verified=True,  # Supabase用户默认已验证
                is_guest=False
            )
            db.add(user)
        else:
            # 更新现有用户
            user.id = UUID(supabase_user_id)  # 更新为Supabase用户ID
            if "username" in user_data:
                user.username = user_data["username"]
            if "name" in user_data:
                user.name = user_data["name"]
            if "age" in user_data:
                user.age = user_data["age"]
            if "bio" in user_data:
                user.bio = user_data["bio"]
            if "avatar_url" in user_data:
                user.avatar_url = user_data["avatar_url"]
            user.is_verified = True  # Supabase用户默认已验证
            user.is_guest = False
        
        db.commit()
        db.refresh(user)
        return user