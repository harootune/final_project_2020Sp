import pandas as pd
from pathlib import Path

DATE_CODES = ['2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6', '2019-7', '2019-8', '2019-9', '2019-10',
          '2019-11', '2019-12', '2020-1', '2020-2']

DISTRICTS = ["Aleppo", "Al-Hasakeh", "Ar-Raqqa", "As-Sweida", "Damascus", "Dar'a", "Deir-ez-Zor",
             "Hama", "Homs", "Idleb", "Lattakia", "Quneitra", "Rural Damascus", "Tartous"]


def extract_conflict_data(conflict_data: pd.DataFrame, admin_district: str, event_type: str):
    """

    :param conflict_data:
    :param admin_district:
    :param event_type:
    :return:
    """
    # Stacking and unstacking inspired by this post: https://stackoverflow.com/questions/37003100/pandas-groupby-for-zero-values

    if admin_district and event_type:
        extracted_conflict_data = conflict_data.groupby(['admin1', 'event_type', 'date_code']).count()['iso'].unstack(fill_value=0).stack()
        extracted_conflict_data = extracted_conflict_data.loc[admin_district, event_type].loc[DATE_CODES]
    elif admin_district:
        extracted_conflict_data = conflict_data.groupby(['admin1', 'date_code']).count()['iso'].unstack(fill_value=0).stack()
        extracted_conflict_data = extracted_conflict_data.loc[admin_district].loc[DATE_CODES]
    elif event_type:
        extracted_conflict_data = conflict_data.groupby(['event_type', 'date_code']).count()['iso'].unstack(fill_value=0).stack()
        extracted_conflict_data = extracted_conflict_data.loc[event_type].loc[DATE_CODES]
    else:
        extracted_conflict_data = conflict_data.groupby(['date_code']).count()['iso']
        extracted_conflict_data = extracted_conflict_data.loc[DATE_CODES]

    return pd.DataFrame(extracted_conflict_data)


def extract_idp_data(idp_data: pd.DataFrame, admin_district: str) -> pd.DataFrame:
    """

    :param idp_data:
    :param admin_district:
    :return:
    """

    if admin_district:
        extracted_idp_data = idp_data.loc[admin_district]
    else:
        extracted_idp_data = idp_data.loc['Grand Total']

    return extracted_idp_data


def calculate_conflict_movement_correlation(conflict_data: pd.DataFrame, idp_data: pd.DataFrame,
                                            event_type: str = '', admin_district: str = ''):
    """

    :param conflict_data:
    :param idp_data:
    :param event_type:
    :param admin_district:
    :return:
    """
    extracted_conflict_data = extract_conflict_data(conflict_data, admin_district, event_type)
    extracted_idp_data = extract_idp_data(idp_data, admin_district)
    corr_frame = extracted_conflict_data.join(extracted_idp_data)
    print(corr_frame.corr())


def main() -> None:
    """

    :return:
    """
    event_type = None
    admin_district = 'Deir-ez-Zor'

    # Data preprocessing - this is unavoidable due to the sheer variability of the source data files
    ## preprocess conflict data
    conflict_data_path = Path('data/conflict_data_syr.csv')
    conflict_data = pd.read_csv(conflict_data_path, index_col='data_id')

    ### Date processing
    conflict_data['event_date'] = pd.to_datetime(conflict_data['event_date'])
    conflict_data['month'] = conflict_data.apply(lambda row: row['event_date'].month, axis=1)
    conflict_data['month'] = conflict_data['month'].astype(str)
    conflict_data['year'] = conflict_data['year'].astype(str)
    conflict_data['date_code'] = conflict_data['year'] + '-' + conflict_data['month']


    ## preprocess IDP movement data
    idp_data_paths = ['data/01_idp_jan_19.xlsx', 'data/02_idp_feb_19.xlsm', 'data/03_idp_mar_19.xlsm',
                      'data/04_idp_apr_19.xlsm', 'data/05_idp_may_19.xlsm', 'data/06_idp_jun_19.xlsm',
                      'data/07_idp_jul_19.xlsm', 'data/08_idp_aug_19.xlsx', 'data/09_idp_sep_19.xlsx',
                      'data/10_idp_oct_19.xlsx', 'data/11_idp_nov_19.xlsx', 'data/12_idp_dec_19.xlsx',
                      'data/13_idp_jan_20.xlsx', 'data/14_idp_feb_20.xlsx']
    idp_data = pd.DataFrame(index=DISTRICTS + ["Unknown", "Grand Total"])

    for i in range(len(idp_data_paths)):
        path = idp_data_paths[i]
        month_data = pd.read_excel(path, sheet_name='Table-Origin_vs_Departure', index_col='Origin')["Grand Total"]
        idp_data = idp_data.join(month_data, rsuffix=str(i))

    ### re-label columns and drop unknown
    idp_data = idp_data.drop(labels='Unknown')  # TODO: DON'T FORGET TO MENTION THAT THIS IS BEING DROPPED
    idp_data.columns = DATE_CODES

    for district in DISTRICTS:
        calculate_conflict_movement_correlation(conflict_data, idp_data, admin_district=district)


main()
