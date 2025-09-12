import os
import pathlib
import functools
import logging

import pandas
import sqlalchemy
from sqlalchemy import update, MetaData, Table, Coloumn

logger: logging.Logger = logging.getLogger(__name__)

class AutoSegmentationGroupsData:
    def get_group_data(self, user_id: int, csv_file="res/default_segment_regions.csv") -> pandas.DataFrame:
        groups: pandas.DataFrame | None = self.read_database(user_id)
        if groups is None:
            groups: pandas.DataFrame = self.read_default_groups(user_id, csv_file)
        return groups

    @functools.lru_cache(maxsize=128, typed=False)
    def read_default_groups(self, user_id, csv_file) -> pandas.DataFrame:
        data: pandas.DataFrame = pandas.read_csv(csv_file)
        for column in data.columns:
            data[column]: str = data[column].str.strip()
        data["user_id"]: int = user_id
        data.set_index(["user_id", "BodySection", "OrganSystem", "Structure"])
        return data

    def get_database_engine(self, db_file="OnkoDICOM.db") -> sqlalchemy.engine.Engine:
        database_file: pathlib.Path = pathlib.Path(os.environ["USER_ONKODICOM_HIDDEN"]).joinpath(db_file)
        return sqlalchemy.create_engine("sqlite:///{}".format(database_file))

    def read_database(self, user_id) -> pandas.DataFrame | None:
        temp_dataframe: pandas.DataFrame | None = None
        with self.get_database_engine().connect() as connection:
            if connection.dialect.has_table(connection, "DefaultSegmentationsRegions"):
                temp_dataframe: pandas.DataFrame = pandas.read_sql_table(table_name="DefaultSegmentationsRegions", con=connection)
                temp_dataframe: pandas.DataFrame = temp_dataframe.loc[temp_dataframe["user_id"] == user_id]
        if temp_dataframe is None:
            return None
        if temp_dataframe.empty:
            return None
        return temp_dataframe

    def save_to_sql(self, groups: pandas.DataFrame) -> int | None:
        with self.get_database_engine().connect() as connection:
            result: int | None = groups.to_sql(name="DefaultSegmentationsRegions", con=connection, if_exists="append")
            if result is ValueError:
                logger.error("Auto Segmentation Groups did not save")
                print("Auto Segmentation Groups: Saving Error")


