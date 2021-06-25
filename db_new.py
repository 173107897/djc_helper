from __future__ import annotations

from const import db_top_dir
from data_struct import ConfigInterface
from util import *


class DbInterface(ConfigInterface):
    # ----------------- 通用字段定义 -----------------
    def __init__(self):
        self.context = "global"
        self.db_type_name = self.__class__.__name__
        self.create_at = format_now()
        self.update_at = format_now()
        self.file_created = False

    # ----------------- 数据库读写操作 -----------------
    def with_context(self, context: str) -> DbInterface:
        """
        设置context，默认为global，修改后保存的key将变更
        """
        self.context = context

        return self

    def load_db(self) -> DbInterface:
        db_file = self.prepare_env_and_get_db_filepath()

        # 若文件存在则加载到内存中
        if os.path.isfile(db_file):
            try:
                self.load_from_json_file(db_file)
            except Exception as e:
                logger.error(f"读取数据库失败，将重置该数据库 context={self.context} db_type_name={self.db_type_name} db_file={db_file}", exc_info=e)
                self.save_db()

        return self

    def save_db(self):
        db_file = self.prepare_env_and_get_db_filepath()
        try:
            if not os.path.isfile(db_file):
                self.create_at = format_now()
                self.file_created = True
            self.update_at = format_now()

            self.save_to_json_file(db_file)
        except Exception as e:
            logger.error(f"保存数据库失败，db_to_save={self}")

    def update_db(self, op: Callable[[Any], Any]) -> Any:
        # 加载配置
        self.load_db()
        # 回调
        res = op(self)
        # 保存修改后的配置
        self.save_db()

        # 返回回调结果
        return res

    # ----------------- 辅助函数 -----------------

    def prepare_env_and_get_db_filepath(self) -> str:
        """
        逻辑说明
        假设key的md5为md5
        本地缓存文件路径为.first_run/md5{0:3}/md5.json
        文件内容为val_type的实例的json序列化结果
        :return: 是否是首次运行
        """
        key_md5 = self.get_db_filename()

        db_dir = os.path.join(db_top_dir, key_md5[0:3])
        db_file = os.path.join(db_dir, key_md5)

        make_sure_dir_exists(db_dir)

        return db_file

    def get_db_filename(self) -> str:
        key = f"{self.context}/{self.db_type_name}"
        return md5(key)


def test():
    from db_def import TestDb

    def _test(db: TestDb, save_inc: int, update_inc: int):
        # init
        db.int_val = 1

        # save
        db.int_val += save_inc
        db.save_db()

        assert_load_same(db, 1 + save_inc)

        def _cb(val: TestDb) -> Any:
            val.int_val += update_inc
            return val.int_val

        db.update_db(_cb)

        assert_load_same(db, 1 + save_inc + update_inc)

    def assert_load_same(db: TestDb, expect: int):
        load_db = TestDb().with_context(db.context).load_db()
        assert load_db.int_val == expect

    # 测试全局
    _test(TestDb(), 1, 10)

    # 测试设置context
    _test(TestDb().with_context("test"), 2, 20)


if __name__ == '__main__':
    test()
