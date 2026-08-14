import pymongo

from bson import ObjectId

from .conf import MONGODB, CNT_MIN


class MongoDB:
    def __init__(self):
        self._client = pymongo.MongoClient(MONGODB["host"],
                                           MONGODB["port"],
                                           connect=False)
        self._db = getattr(self._client, MONGODB["db"])

    def get_part(self, s: int, n: int) -> int:
        res = self._db.part.find_one({"s": s, "n": n})
        if res:
            return res["cnt"]
        return -1

    def get_part_ceil(self, s: int, n: int, iteration: int, ceil: int) -> int:
        res = self._db.part_ceil.find_one({"s": s, "n": n, "i": iteration, "c": ceil})
        if res:
            return res["cnt"]
        return -1

    def get_diff(self, s: int, n: int) -> int:
        res = self._db.diff.find_one({"s": s, "n": n})
        if res:
            return res["cnt"]
        return -1

    def get_edge(self, s: int, n: int, iteration: int) -> int:
        res = self._db.edge.find_one({"s": s, "n": n, "i": iteration})
        if res:
            return res["cnt"]
        return -1

    def add_part(self, s: int, n: int, iteration: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return
        self._db.part.insert_one({"s": s, "n": n, "i": iteration, "cnt": cnt})

    def add_part_ceil(self, s: int, n: int, iteration: int, ceil: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return
        self._db.part_ceil.insert_one({"s": s, "n": n, "i": iteration, "c": ceil, "cnt": cnt})

    def add_diff(self, s: int, n: int, cnt: int):
        if cnt < CNT_MIN:
            return
        self._db.diff.insert_one({"s": s, "n": n, "cnt": cnt})

    def add_edge(self, s: int, n: int, iteration: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return
        self._db.edge.insert_one({"s": s, "n": n, "i": iteration, "cnt": cnt})


MongoDBClient = MongoDB()

