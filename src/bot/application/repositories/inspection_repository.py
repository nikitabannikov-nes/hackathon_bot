from datetime import datetime
from typing import list

from bson import ObjectId


class InspectionRepository:
    def __init__(self, mongo_db):
        self.collection = mongo_db.db['inspections']

    async def add_inspection(self, data: dict) -> dict:
        """
        Добавляет новую проверку/инспекцию
        data: {
            "date": datetime.,
            "area": 1,
            "cleaner_id": "user_id_1",
            "inspector_id": "user_id_2",
            "problems": [
                {
                    "id": None,
                    "description": "Проблема 1",
                    "photo_url": "https://..."
                },
                ...
            ]
        }
        """
        document = {
            "date": data.get("date", datetime.now()), #!!!
            "area": data.get("area"),
            "cleaner_id": data.get("cleaner_id"),
            "inspector_id": data.get("inspector_id"),
            "problems": data.get("problems", [])
        }
        result = self.collection.insert_one(document)
        return {"_id": str(result.inserted_id), **document}

    async def get_by_id(self, inspection_id: str) -> dict:
        """
        Получает инспекцию по ObjectId
        """
        inspection = self.collection.find_one({"_id": ObjectId(inspection_id)})
        if not inspection:
            raise ValueError(f"Инспекция с id={inspection_id} не найдена")
        inspection["_id"] = str(inspection["_id"])
        return inspection

    async def get_by_area(self, area: int) -> list:
        """
        Получает все инспекции для определённой области
        """
        inspections = list(self.collection.find({"area": area}))
        for inspection in inspections:
            inspection["_id"] = str(inspection["_id"])
        return inspections

    async def get_by_cleaner_id(self, cleaner_id: str) -> list:
        """
        Получает все инспекции по уборщику
        """
        inspections = list(self.collection.find({"cleaner_id": cleaner_id}))
        for inspection in inspections:
            inspection["_id"] = str(inspection["_id"])
        return inspections

    async def get_by_inspector_id(self, inspector_id: str) -> list:
        """
        Получает все инспекции по инспектору
        """
        inspections = list(self.collection.find({"inspector_id": inspector_id}))
        for inspection in inspections:
            inspection["_id"] = str(inspection["_id"])
        return inspections

    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> list:
        """
        Получает инспекции в диапазоне дат
        """
        inspections = list(self.collection.find({
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }))
        for inspection in inspections:
            inspection["_id"] = str(inspection["_id"])
        return inspections

    # async def add_problem(self, inspection_id: str, problem: dict) -> dict:
    #     """
    #     Добавляет проблему к инспекции
    #     problem: {"id": None, "description": "...", "photo_url": "..."}
    #     """
    #     result = self.collection.find_one_and_update(
    #         {"_id": ObjectId(inspection_id)},
    #         {"$push": {"problems": problem}},
    #         return_document=True
    #     )
    #     if not result:
    #         raise ValueError(f"Инспекция с id={inspection_id} не найдена")
    #     result["_id"] = str(result["_id"])
    #     return result

    # async def update_problem(self, inspection_id: str, problem_index: int, problem_data: dict) -> dict:
    #     """
    #     Обновляет проблему по индексу
    #     """
    #     result = self.collection.find_one_and_update(
    #         {"_id": ObjectId(inspection_id)},
    #         {"$set": {f"problems.{problem_index}": problem_data}},
    #         return_document=True
    #     )
    #     if not result:
    #         raise ValueError(f"Инспекция с id={inspection_id} не найдена")
    #     result["_id"] = str(result["_id"])
    #     return result

    async def delete_problem(self, inspection_id: str, problem_index: int) -> dict:
        """
        Удаляет проблему по индексу
        """
        # Получаем инспекцию
        inspection = self.collection.find_one({"_id": ObjectId(inspection_id)})
        if not inspection:
            raise ValueError(f"Инспекция с id={inspection_id} не найдена")

        # Удаляем проблему по индексу
        problems = inspection.get("problems", [])
        if problem_index < 0 or problem_index >= len(problems):
            raise ValueError(f"Индекс проблемы {problem_index} не валиден")

        problems.pop(problem_index)

        result = self.collection.find_one_and_update(
            {"_id": ObjectId(inspection_id)},
            {"$set": {"problems": problems}},
            return_document=True
        )
        result["_id"] = str(result["_id"])
        return result

    async def get_problems_by_inspection(self, inspection_id: str) -> list:
        """
        Получает все проблемы из инспекции
        """
        inspection = self.collection.find_one({"_id": ObjectId(inspection_id)})
        if not inspection:
            raise ValueError(f"Инспекция с id={inspection_id} не найдена")
        return inspection.get("problems", [])

    async def delete_inspection(self, inspection_id: str) -> bool:
        """
        Удаляет инспекцию по id
        """
        result = self.collection.delete_one({"_id": ObjectId(inspection_id)})
        if result.deleted_count == 0:
            raise ValueError(f"Инспекция с id={inspection_id} не найдена")
        return True
