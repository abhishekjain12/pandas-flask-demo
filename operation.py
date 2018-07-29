import json
import logging
import os

import pandas as pd

from os.path import basename, splitext, dirname, abspath
from logs import logs

module_directory = dirname(__file__)
logs.initialize_logger("operation")


def replace_col_name(replace_col):
    with open(abspath(module_directory + '/Columns_Name.json')) as col_data:
        col_data = json.load(col_data)

        for columnsDetail in col_data['columnsDetail']:
            for possibleValue in columnsDetail['possibleValue']:
                if possibleValue == replace_col:
                    return columnsDetail['columnName']


def drop_col_name(col_name):
    with open(abspath(module_directory + '/Columns_Delete.json')) as col_data:
        col_data = json.load(col_data)

        for columnsDetail in col_data['columnsDetail']:
            if columnsDetail == col_name:
                return True


def remove_files(file_path):
    try:
        os.remove(file_path)
        return True

    except Exception as e:
        logging.error("Failed to remove file. Error message: %s", e)
        return None


def compute_data(file_path, sheet_active=None):
    logging.debug("Inside compute_data function. : " + str(file_path))

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, index_col=None, header=None)

            i = 0
            for count_ in df.count(axis=1):
                if count_ == len(df.columns):
                    break
                else:
                    i += 1

            df.drop(df.index[0:i], inplace=True)

            df.columns = df.iloc[0]
            df.drop(df.index[0], inplace=True)

            for col in list(df):
                is_delete = drop_col_name(col)
                if is_delete:
                    df.drop(col, axis=1, inplace=True)

                else:
                    new_col_name = replace_col_name(col)
                    if new_col_name is not None:
                        df.rename(columns={col: new_col_name}, inplace=True)

            file_name = splitext(basename(file_path))[0]
            df.to_excel(module_directory + "/output_files/output_" + file_name + ".xlsx", index=False)
            logging.debug("Successfully Saved. : " + str(file_path))

            remove_files(file_path)
            return file_name + ".xlsx"

        else:
            with pd.ExcelFile(file_path) as xlsx_file:
                for sheet in xlsx_file.sheet_names:
                    if sheet == sheet_active:
                        df = pd.read_excel(xlsx_file, str(sheet), index_col=None, header=None)

                        i = 0
                        for count_ in df.count(axis=1):
                            if count_ == len(df.columns):
                                break
                            else:
                                i += 1

                        df.drop(df.index[0:i], inplace=True)

                        df.columns = df.iloc[0]
                        df.drop(df.index[0], inplace=True)

                        for col in list(df):
                            is_delete = drop_col_name(col)
                            if is_delete:
                                df.drop(col, axis=1, inplace=True)

                            else:
                                new_col_name = replace_col_name(col)
                                if new_col_name is not None:
                                    df.rename(columns={col: new_col_name}, inplace=True)

                        file_name = splitext(basename(file_path))[0]
                        df.to_excel(module_directory + "/output_files/output_" + file_name + ".xlsx", index=False)
                        logging.debug("Successfully Saved. : " + str(file_path))

                        remove_files(file_path)
                        return file_name + ".xlsx"

                    else:
                        logging.debug("Sheet name is not matched. : " + str(file_path))
                        remove_files(file_path)
                        return None

    except Exception as e:
        logging.error("Error in operation function. : " + str(file_path) + " Error Message: %s", e)
        return None
