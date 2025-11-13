from datetime import datetime

from bson import ObjectId


class CheckListRepository:
    def __init__(self, mongo_db):
        self.collection = mongo_db.db['checklists']

    async def add_checklist(self, data: dict) -> dict:
        """
        Добавляет новый чек-лист
        data: {
            "name": "Форма 2_...",
            "area": 1,
            "items": [{"type": "A", "order": 1, "description": "...", "mark": False}, ...]
        }
        """
        document = {
            "name": data.get("name"),
            "area": data.get("area"),
            "items": data.get("items", []),
            "created_at": datetime.now()
        }
        result = self.collection.insert_one(document)
        return {"_id": str(result.inserted_id), **document}

    async def get_by_id(self, checklist_id: str) -> dict:
        """
        Получает чек-лист по ObjectId
        """
        checklist = self.collection.find_one({"_id": ObjectId(checklist_id)})
        if not checklist:
            raise ValueError(f"Чек-лист с id={checklist_id} не найден")
        checklist["_id"] = str(checklist["_id"])
        return checklist

    async def get_by_name(self, name: str) -> dict:
        """
        Получает чек-лист по названию
        """
        checklist = self.collection.find_one({"name": name})
        if not checklist:
            raise ValueError(f"Чек-лист с названием={name} не найден")
        checklist["_id"] = str(checklist["_id"])
        return checklist

    async def get_by_area(self, area: int) -> list:
        """
        Получает все чек-листы для определённой области
        """
        checklists = list(self.collection.find({"area": area}))
        for checklist in checklists:
            checklist["_id"] = str(checklist["_id"])
        return checklists

    # async def add_item_to_checklist(self, checklist_id: str, item: dict) -> dict:
    #     """
    #     Добавляет элемент в чек-лист
    #     item: {"type": "A", "order": 1, "description": "...", "mark": False}
    #     """
    #     result = self.collection.find_one_and_update(
    #         {"_id": ObjectId(checklist_id)},
    #         {"$push": {"items": item}},
    #         return_document=True
    #     )
    #     if not result:
    #         raise ValueError(f"Чек-лист с id={checklist_id} не найден")
    #     result["_id"] = str(result["_id"])
    #     return result

    async def update_item_mark(self, checklist_id: str, item_order: int, mark: bool = 1) -> dict:
        """
        Обновляет статус (mark) элемента в чек-листе по порядковому номеру
        """
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(checklist_id), "items.order": item_order},
            {"$set": {"items.$.mark": mark}},
            return_document=True
        )
        if not result:
            raise ValueError(f"Элемент с order={item_order} не найден в чек-листе {checklist_id}")
        result["_id"] = str(result["_id"])
        return result

    # async def get_items_by_type(self, checklist_id: str, item_type: str) -> list:
    #     """
    #     Получает все элементы определённого типа (A/B/C) из чек-листа
    #     """
    #     checklist = self.collection.find_one({"_id": ObjectId(checklist_id)})
    #     if not checklist:
    #         raise ValueError(f"Чек-лист с id={checklist_id} не найден")
    #
    #     items = [item for item in checklist.get("items", []) if item.get("type") == item_type]
    #     return items

    # async def get_checked_items(self, checklist_id: str) -> list:
    #     """
    #     Получает все отмеченные элементы (mark=True)
    #     """
    #     checklist = self.collection.find_one({"_id": ObjectId(checklist_id)})
    #     if not checklist:
    #         raise ValueError(f"Чек-лист с id={checklist_id} не найден")
    #
    #     items = [item for item in checklist.get("items", []) if item.get("mark")]
    #     return items

    async def delete_checklist(self, checklist_id: str) -> bool:
        """
        Удаляет чек-лист по id
        """
        result = self.collection.delete_one({"_id": ObjectId(checklist_id)})
        if result.deleted_count == 0:
            raise ValueError(f"Чек-лист с id={checklist_id} не найден")
        return True

    async def delete_item(self, checklist_id: str, item_order: int) -> dict:
        """
        Удаляет элемент из чек-листа по порядковому номеру
        """
        result = self.collection.find_one_and_update(
            {"_id": ObjectId(checklist_id)},
            {"$pull": {"items": {"order": item_order}}},
            return_document=True
        )
        if not result:
            raise ValueError(f"Чек-лист с id={checklist_id} не найден")
        result["_id"] = str(result["_id"])
        return result
