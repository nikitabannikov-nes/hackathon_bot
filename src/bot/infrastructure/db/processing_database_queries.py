from sqlalchemy.orm import Session
from models import User
from postgra_client import engine


def add_user_from_dict(data: dict):
    session = Session(engine)

    try:
        full_name = data.get('full_name', '').strip()
        parts = full_name.split()

        if len(parts) != 3:
            raise ValueError(f"full_name должен содержать 3 части (фамилия имя отчество), получено: {len(parts)}")

        surname = parts[0]
        name = parts[1]
        fathername = parts[2]
        role = data.get('role')
        username = data.get('username')
        team = data.get('team')


        if not all([surname, name, fathername, role, username, team]):
            raise ValueError("Отсутствуют обязательные данные в словаре")


        exists = session.query(User).filter(
            User.surname == surname,
            User.name == name,
            User.fathername == fathername,
            User.role == role,
            User.username == username,
            User.team == team
        ).first()

        if exists:
            raise ValueError("Пользователь с такими данными уже существует")

        # Создаем нового пользователя
        new_user = User(
            surname=surname,
            name=name,
            fathername=fathername,
            role=role,
            username=username,
            team=team,
            area=data.get('area')  # опциональное поле
        )

        session.add(new_user)
        session.commit()

        print(f"Пользователь {surname} {name} {fathername} успешно добавлен")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
