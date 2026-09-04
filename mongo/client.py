import pymongo
import logging

from abc import ABC, abstractmethod

from .conf import MONGODB, CNT_MIN, ENV


logger = logging.getLogger('mongo')


class MongoAbstractDB(ABC):
    @abstractmethod
    def init_db(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_part(self, s: int, n: int) -> int:
        return 0

    @abstractmethod
    def get_part_ceil(self, s: int, n: int, iteration: int, ceil: int) -> int:
        return 0

    @abstractmethod
    def get_diff(self, s: int, n: int) -> int:
        return 0

    @abstractmethod
    def get_edge(self, s: int, n: int, iteration: int) -> int:
        return 0

    @abstractmethod
    def add_part(self, s: int, n: int, iteration: int, cnt: int):
        pass

    @abstractmethod
    def add_part_ceil(self, s: int, n: int, iteration: int, ceil: int, cnt: int):
        pass

    @abstractmethod
    def add_diff(self, s: int, n: int, cnt: int):
        pass

    @abstractmethod
    def add_edge(self, s: int, n: int, iteration: int, cnt: int):
        pass


class MongoMockDB(MongoAbstractDB):
    def init_db(self):
        pass

    def close(self):
        pass

    def get_part(self, s: int, n: int) -> int:
        return 0

    def get_part_ceil(self, s: int, n: int, iteration: int, ceil: int) -> int:
        return 0

    def get_diff(self, s: int, n: int) -> int:
        return 0

    def get_edge(self, s: int, n: int, iteration: int) -> int:
        return 0

    def add_part(self, s: int, n: int, iteration: int, cnt: int):
        pass

    def add_part_ceil(self, s: int, n: int, iteration: int, ceil: int, cnt: int):
        pass

    def add_diff(self, s: int, n: int, cnt: int):
        pass

    def add_edge(self, s: int, n: int, iteration: int, cnt: int):
        pass


class MongoDB(MongoAbstractDB):
    def __init__(self):
        self._client = pymongo.MongoClient(MONGODB["host"],
                                           MONGODB["port"],
                                           connect=False)
        self._db = getattr(self._client, MONGODB["db"])

    def init_db(self):
        #self._db.create_collection("part")
        #self._db.create_collection("part_ceil")
        #self._db.create_collection("diff")
        #self._db.create_collection("edge")

        part = self._db.part
        part_ceil = self._db.part_ceil
        diff = self._db.diff
        edge = self._db.edge

        # 1 - pymongo.ASCENDING, -1 - pymongo.DESCENDING
        idx = part.create_index([("s", 1), ("n", 1)], unique=True)
        print(f"Created unique compound index: {idx}")
        idx = part_ceil.create_index([("s", 1), ("n", 1), ("i", 1), ("c", 1)], unique=True)
        print(f"Created unique compound index: {idx}")
        idx = diff.create_index([("s", 1), ("n", 1)], unique=True)
        print(f"Created unique compound index: {idx}")
        idx = edge.create_index([("s", 1), ("n", 1), ("i", 1)], unique=True)
        print(f"Created unique compound index: {idx}")

    def close(self):
        self._client.close()

    def get_part(self, s: int, n: int) -> int:
        res = self._db.part.find_one({"s": s, "n": n})
        if res:
            return res["cnt"]
        return 0

    def get_part_ceil(self, s: int, n: int, iteration: int, ceil: int) -> int:
        res = self._db.part_ceil.find_one({"s": s, "n": n, "i": iteration, "c": ceil})
        if res:
            return res["cnt"]
        return 0

    def get_diff(self, s: int, n: int) -> int:
        res = self._db.diff.find_one({"s": s, "n": n})
        if res:
            return res["cnt"]
        return 0

    def get_edge(self, s: int, n: int, iteration: int) -> int:
        res = self._db.edge.find_one({"s": s, "n": n, "i": iteration})
        if res:
            return res["cnt"]
        return 0

    def add_part(self, s: int, n: int, iteration: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return

        doc = {"s": s, "n": n, "i": iteration, "cnt": cnt}
        try:
            self._db.part.insert_one(doc)
        except pymongo.errors.DuplicateKeyError as err:
            logger.info(f"doc already exists: {doc}")
            _cnt = self.get_part(s, n)
            logger.info(f"cnt in doc: {_cnt}")
            logger.info(f"cnt inserted: {cnt}")
            logger.error(err)

    def add_part_ceil(self, s: int, n: int, iteration: int, ceil: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return

        doc = {"s": s, "n": n, "i": iteration, "c": ceil, "cnt": cnt}
        try:
            self._db.part_ceil.insert_one(doc)
        except pymongo.errors.DuplicateKeyError as err:
            logger.info(f"doc already exists: {doc}")
            _cnt = self.get_part_ceil(s, n, iteration, ceil)
            logger.info(f"cnt in doc: {_cnt}")
            logger.info(f"cnt inserted: {cnt}")
            logger.error(err)

    def add_diff(self, s: int, n: int, cnt: int):
        if cnt < CNT_MIN:
            return

        doc = {"s": s, "n": n, "cnt": cnt}
        try:
            self._db.diff.insert_one(doc)
        except pymongo.errors.DuplicateKeyError as err:
            logger.info(f"doc already exists: {doc}")
            _cnt = self.get_diff(s, n)
            logger.info(f"cnt in doc: {_cnt}")
            logger.info(f"cnt inserted: {cnt}")
            logger.error(err)

    def add_edge(self, s: int, n: int, iteration: int, cnt: int):
        """
        assume term_idx = 0
        """
        if cnt < CNT_MIN:
            return

        doc = {"s": s, "n": n, "i": iteration, "cnt": cnt}
        try:
            self._db.edge.insert_one(doc)
        except pymongo.errors.DuplicateKeyError as err:
            logger.info(f"doc already exists: {doc}")
            _cnt = self.get_edge(s, n, iteration)
            logger.info(f"cnt in doc: {_cnt}")
            logger.info(f"cnt inserted: {cnt}")
            logger.error(err)


MongoClient = None


def get_client() -> MongoDB | MongoMockDB:
    global MongoClient
    if MongoClient is None:
        if ENV == "DEV":
            MongoClient = MongoMockDB()
        else:
            MongoClient = MongoDB()
    return MongoClient
