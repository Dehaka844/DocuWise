from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.database_models.user import User
from app.database_models.department import Department


class UserService:

    ADMIN_MUTATION_LOCK_KEY = 684728341

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

    def get_user_by_email(
        self,
        email: str,
    ) -> User | None:

        statement = select(User).where(
            User.email == email
        )

        return self.db.scalar(
            statement
        )

    def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:

        statement = (
            select(User)
            .where(User.id == user_id)
            .execution_options(populate_existing=True)
        )

        return self.db.scalar(
            statement
        )

    def lock_admin_mutations(self) -> None:
        self.db.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": self.ADMIN_MUTATION_LOCK_KEY},
        )

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        departments: list[str] | None = None,
    ) -> User:

        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
        )
        if departments:
            user.departments = list(
                self.db.scalars(
                    select(Department).where(Department.code.in_(departments))
                ).all()
            )

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    def get_users(self) -> list[User]:
        statement = (
            select(User)
            .options(selectinload(User.departments))
            .order_by(User.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def count_active_admins(
        self,
        excluding_user_id: int | None = None,
    ) -> int:
        statement = select(func.count()).select_from(User).where(
            User.role == "admin",
            User.is_active.is_(True),
        )

        if excluding_user_id is not None:
            statement = statement.where(User.id != excluding_user_id)

        return self.db.scalar(statement) or 0

    def update_access(
        self,
        user: User,
        role: str | None,
        is_active: bool | None,
        departments: list[str] | None = None,
    ) -> User:
        if role is not None:
            user.role = role

        if is_active is not None:
            user.is_active = is_active

        if departments is not None:
            user.departments = list(
                self.db.scalars(
                    select(Department).where(Department.code.in_(departments))
                ).all()
            )

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
