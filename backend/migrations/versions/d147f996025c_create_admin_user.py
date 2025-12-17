"""create_admin_reader

Revision ID: d147f996025c
Revises: 5be7d268373e
Create Date: 2025-12-17 18:16:40.999302

"""
import hashlib
import os
from typing import Any, Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


import os
import sys
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'))
from app.utils.auth.oauth2 import OAuth2Utility
from app.models.types import Role


revision: str = "d147f996025c"
down_revision: Union[str, Sequence[str], None] = "5be7d268373e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создание администратора в таблице readers"""
    
    admin_email = os.getenv('ADMIN_EMAIL', '123@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', '12341234')
    
    conn = op.get_bind()
    
    result = conn.execute(
        sa.text("SELECT COUNT(*) FROM readers WHERE email = :email"),
        {"email": admin_email}
    ).fetchone()[0] # type: ignore
    
    if result == 0:
        try:
            result = conn.execute(sa.text("""
                INSERT INTO readers (email, role, encrypted_password, verified) 
                VALUES (:email, :role, :password, :verified) 
                RETURNING id
            """), {
                "email": admin_email,
                "role": Role.ADMIN.value,
                "password": OAuth2Utility.get_hashed_password(admin_password),
                "verified": True,
            }).fetchone()
            
            admin_id = result[0] # type: ignore
            
            # **3. Создаем профиль**
            conn.execute(sa.text("""
                INSERT INTO profiles (reader_id, avatar_url, full_name) 
                VALUES (:reader_id, NULL, :full_name)
            """), {
                "reader_id": admin_id,
                "full_name": "Администратор библиотеки",
            })
            
            print(f"✅ Администратор создан:")
            print(f"   📧 {admin_email}")
            print(f"   🔑 {admin_password}")
            print(f"   🆔 {admin_id}")
            
        except Exception as e:
            print(f"❌ Ошибка создания админа: {e}")
            raise
    else:
        print(f"ℹ️  Администратор {admin_email} уже существует")


def downgrade() -> None:
    """Удаление администратора"""
    admin_email = os.getenv('ADMIN_EMAIL', '123@example.com')
    
    conn = op.get_bind()
    
    # Удаляем профиль
    conn.execute(
        sa.text("""
            DELETE FROM profiles 
            WHERE reader_id IN (
                SELECT id FROM readers WHERE email = :email
            )
        """),
        { "email": admin_email }
    )
    
    # Удаляем читателя
    conn.execute(
        sa.text("DELETE FROM readers WHERE email = :email"),
        { "email": admin_email }
    )
    
    print(f"🗑️  Администратор {admin_email} удален")
