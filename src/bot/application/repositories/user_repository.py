from sqlalchemy import select
from src.bot.infrastructure.db.models.models import User


class UserRepository:

    async def exists(self, session, id: str) -> bool:
        """
        Проверяет существование пользователя по id
        """

        result = await session.execute(
            select(User).where(User.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def get_user_role(self, session, id: str) -> str:
        """
        Получает роль пользователя по id
        """
        result = await session.execute(
            select(User.role).where(User.id == id)
        )
        role = result.scalar_one_or_none()
        if role is None:
            raise ValueError(f"Пользователь с id={id} не найден")
        return role

    async def add_user_from_dict(self, session,data: dict) -> User:
        full_name = data.get('full_name', '').strip()
        parts = full_name.split()
        if len(parts) != 3:
            raise ValueError("full_name должен содержать три части: фамилия, имя, отчество")

        surname, name, fathername = parts
        role = data.get('role')
        username = data.get('username')
        team = data.get('team')
        id=data.get('user_id')
        area = data.get('area')

        if not all([surname, name, fathername, role, username, team, ]):
            raise ValueError("Отсутствуют обязательные поля")

        # Проверяем существование пользователя
        stmt = select(User).where(
            (User.id == id)
        )


        result = await session.execute(stmt)
        exists = result.scalar_one_or_none()

        if exists:
            raise ValueError("Пользователь с такими данными уже существует")

            # Создаём и добавляем нового пользователя
        new_user = User(
            id=id,
            surname=surname,
            name=name,
            fathername=fathername,
            role=role,
            username=username,
            team=team,
            area=area
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user




