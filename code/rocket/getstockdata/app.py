# coding:utf-8

from typing import Union, List

from apscheduler.schedulers.blocking import BlockingScheduler

from db_utils import DBUtils
from get_data import GetData
from db_init import DB_init
from read_file import get_stock_symbols


def update_realtime(symbols: Union[str, List[str]]):
    DBUtils.save_realtime(GetData.get_real_time_price(symbols))


def update_daily(symbols: Union[str, List[str]]):
    DBUtils.save_daily_history(GetData.get_daily_data(symbols))


if __name__ == '__main__':
    print(get_stock_symbols())
    DB_init(get_stock_symbols())

    scheduler = BlockingScheduler()
    scheduler.add_job(update_realtime, 'interval', seconds=5, args=[get_stock_symbols(), ])
    scheduler.add_job(update_daily, 'interval', seconds=70, args=[get_stock_symbols(), ])
    try:
        scheduler.start()
    except SystemExit:
        pass
