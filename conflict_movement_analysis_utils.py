"""
This module is intended to partially fulfill the requirements for the IS 590PR Spring final

Intended to support conflict_and_movement_in_syria_2019-2020.ipynb

Running as a main will print a small demonstration of correlation analysis using the functions in this module.

Name: conflict_movement_analysis_utils.py
Date (MM-DD-YYYY): 04-29-2020
Author: Derek Harootune Otis (They/Them)
"""


import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def clean_conflict_data(conflict_data_path: str) -> pd.DataFrame:
    """
    This program produces a dataframe from a conflict data file (as produced by the Armed Conflict Location & Event
    Data project), makes the dataframe compatible with correlation analysis functions defined in this module, and
    returns a reference to the dataframe.

    :param conflict_data_path: a path to an ACLED data file
    :return: a dataframe containing information from the ACLED file adjusted for inter-function compatibility
    >>> conflict_data = clean_conflict_data('data/conflict_data_syr.csv')
    >>> conflict_data['event_date'].dtype #doctest: +NORMALIZE_WHITESPACE
        dtype('<M8[ns]')
    >>> conflict_data.iloc[0]['date_code'] #doctest: +NORMALIZE_WHITESPACE
        '2020-3'
    """
    conflict_data_path = Path(conflict_data_path)
    conflict = pd.read_csv(conflict_data_path, index_col='data_id')

    # Date processing
    conflict['event_date'] = pd.to_datetime(conflict['event_date'])
    conflict['month'] = conflict.apply(lambda row: row['event_date'].month, axis=1)
    conflict['month'] = conflict['month'].astype(str)
    conflict['year'] = conflict['year'].astype(str)
    conflict['date_code'] = conflict['year'] + '-' + conflict['month']

    return conflict


def aggregate_idp_data(idp_data_paths: list, date_codes: list, districts: list) -> pd.DataFrame:
    """
    Aggregates a dataframe containing IDP movement totals within a certain date-range from a series of IDP movement
    monthly reports produced by OCHA Turkey. The dataframe is made for inter-function compatibility within this file.

    IMPORT NOTE: Counts of movement from "Unknown" origins are dropped, but are implicitly included in grand totals
    of IDP movement for the entire country.

    :param idp_data_paths: a list of paths to IDP movement data files per month. PATH ORDER MUST MATCH DATE CODES
    :param date_codes: a list of date codes for each month of data
    :param districts: a list of districts which the IDP movement data can be mapped to
    :return: a dataframe containing information from the IDP movement data files

    >>> data_paths = ['test/idp_1.xlsx', 'test/idp_2.xlsx']
    >>> date_codes = ['2030-1', '2030-2']
    >>> districts = ["Aleppo", "Al-Hasakeh", "Ar-Raqqa", "As-Sweida", "Damascus", "Dar'a", "Deir-ez-Zor","Hama", \
        "Homs", "Idleb", "Lattakia", "Quneitra", "Rural Damascus", "Tartous"]
    >>> print(aggregate_idp_data(data_paths, date_codes, districts).loc['Aleppo']) #doctest: +NORMALIZE_WHITESPACE
    2030-1    3.0
    2030-2    2.0
    Name: Aleppo, dtype: float64

    """
    idp = pd.DataFrame(index=districts + ["Unknown", "Grand Total"])

    for i in range(len(idp_data_paths)):
        path = idp_data_paths[i]
        month_data = pd.read_excel(path, sheet_name='Table-Origin_vs_Departure', index_col='Origin')["Grand Total"]
        idp = idp.join(month_data, rsuffix=str(i))

    # re-label columns and drop unknown
    idp = idp.drop(labels='Unknown')
    idp.columns = date_codes

    return idp


def extract_conflict_data(conflict_data: pd.DataFrame, date_codes: list, admin_district: str, event_type: str,
                          party: str, fatal: bool = False) -> pd.DataFrame:
    """
    Extracts a subset of conflict data from a dataframe produced by clean_conflict_data, based on a number of
    flags defined through kwargs, and returns it as a dataframe.

    :param conflict_data: a dataframe produced by clean_conflict_data
    :param date_codes: date codes for all months within the range of time being analyzed
    :param admin_district: selects a specific district to extract data for
    :param event_type: selects a specific conflict event type to extract data for
    :param party: selects a specific party to extract data for
    :param fatal: if True, counts number of fatalities instead of number of events
    :return: a dataframe containing the specified subset
    """
    # Stacking and unstacking inspired by this post: https://stackoverflow.com/questions/37003100/pandas-groupby-for-zero-values

    extracted_conflict_data = conflict_data

    if party:
        extracted_conflict_data['filter1'] = extracted_conflict_data['actor1'].str.contains(party, na=False)
        extracted_conflict_data['filter2'] = extracted_conflict_data['actor2'].str.contains(party, na=False)
        extracted_conflict_data = conflict_data.query('filter1 or filter2')

    if admin_district and event_type:
        if fatal:
            extracted_conflict_data = extracted_conflict_data.groupby(['admin1', 'event_type', 'date_code']).sum()[
                'fatalities'].unstack(fill_value=0).stack()
        else:
            extracted_conflict_data = extracted_conflict_data.groupby(['admin1', 'event_type', 'date_code']).count()[
                'iso'].unstack(fill_value=0).stack()

        extracted_conflict_data = extracted_conflict_data.loc[admin_district, event_type].loc[date_codes]

    elif admin_district:
        if fatal:
            extracted_conflict_data = extracted_conflict_data.groupby(['admin1', 'date_code']).sum()['fatalities'].unstack(
                fill_value=0).stack()
        else:
            extracted_conflict_data = extracted_conflict_data.groupby(['admin1', 'date_code']).count()['iso'].unstack(
                fill_value=0).stack()

        extracted_conflict_data = extracted_conflict_data.loc[admin_district].loc[date_codes]

    elif event_type:
        if fatal:
            extracted_conflict_data = extracted_conflict_data.groupby(['event_type', 'date_code']).sum()['fatalities'].unstack(
                fill_value=0).stack()
        else:
            extracted_conflict_data = extracted_conflict_data.groupby(['event_type', 'date_code']).count()['iso'].unstack(
                fill_value=0).stack()

        extracted_conflict_data = extracted_conflict_data.loc[event_type].loc[date_codes]

    else:
        if fatal:
            extracted_conflict_data = extracted_conflict_data.groupby(['date_code']).sum()['fatalities']
        else:
            extracted_conflict_data = extracted_conflict_data.groupby(['date_code']).count()['iso']

        extracted_conflict_data = extracted_conflict_data.loc[date_codes]

    return pd.DataFrame(extracted_conflict_data)


def extract_idp_data(idp_data: pd.DataFrame, admin_district: str) -> pd.DataFrame:
    """
    Extracts a subset of IDP movement data from a dataframe produced by aggregate_idp_data, either a grand total or a
    specified district.

    :param idp_data: a dataframe produced by aggregate_idp_data
    :param admin_district: a specific administrative district to select data for
    :return: a dataframe containing the specified subset
    """
    if admin_district:
        extracted_idp_data = idp_data.loc[admin_district]
    else:
        extracted_idp_data = idp_data.loc['Grand Total']

    return extracted_idp_data


def calculate_conflict_movement_correlation(conflict_data: pd.DataFrame, idp_data: pd.DataFrame, date_codes: list,
                                            event_type: str = '', admin_district: str = '', party: str = '',
                                            delta: bool = False, fatal: bool = False) -> pd.DataFrame:
    """


    :param conflict_data: a dataframe produced by clean_conflict_data
    :param idp_data: a dataframe produced by aggregate_idp_data
    :param date_codes: date codes for all months within the range of time being analyzed
    :param event_type: selects a specific conflict event type to extract data for
    :param admin_district: selects a specific district to extract data for
    :param party: selects a specific party to extract data for
    :param delta:if True, calculates correlation for percent change in variables between months
    :param fatal: if True, counts number of fatalities instead of number of events
    :return: A dataframe describing the correlation of movement and conflict within the data subset selected
    """
    extracted_conflict_data = extract_conflict_data(conflict_data, date_codes,
                                                    admin_district, event_type, party, fatal=fatal)

    extracted_idp_data = extract_idp_data(idp_data, admin_district)

    corr_frame = extracted_conflict_data.join(extracted_idp_data)

    if delta:
        corr_frame = corr_frame.pct_change()
        corr_frame = corr_frame.drop(labels='2019-1')

    labels = {'iso': 'conflict', 'fatalities': 'conflict', 'Grand Total': 'movement'}
    corr_frame = corr_frame.corr().rename(columns=labels, index=labels)

    return corr_frame


def district_wise_correlations(districts: list, conflict_data: pd.DataFrame, idp_data: pd.DataFrame, date_codes: list,
                               event_type: str = '', party: str = '', delta: bool = False, fatal: bool = False) -> pd.DataFrame:
    """

    :param districts: a list of districts to produce calculate correlation statistics for
    :param conflict_data: a dataframe produced by clean_conflict_data
    :param idp_data: a dataframe produced by aggregate_idp_data
    :param date_codes: date codes for all months within the range of time being analyzed
    :param event_type: selects a specific conflict event type to extract data for
    :param party: selects a specific party to extract data for
    :param delta:if True, calculates correlation for percent change in variables between months
    :param fatal: if True, counts number of fatalities instead of number of events
    :return: None
    """
    district_wise_frame = pd.DataFrame(index=districts, columns=['correlation'])

    for district in districts:
        district_wise_frame.loc[district] = calculate_conflict_movement_correlation(conflict_data, idp_data, date_codes,
                                                                             admin_district=district,
                                                                             party=party,
                                                                             event_type=event_type,
                                                                             delta=delta,
                                                                             fatal=fatal).loc[district][0]

    return district_wise_frame


def display_cm_correlation_bar_graph(district_correlations: pd.DataFrame, title: str, x_label: str = 'Governorate',
                                     y_label: str = 'Correlation') -> None:
    """
    Plots a bar graph representing various district wise correlations produced by district_wise_correlations

    :param district_correlations: a dataframe produced by district_wise_correlations
    :param title: title of the resulting bar graph
    :param x_label: An optional label for the x-axis
    :param y_label: An optional label for the y-axis
    :return: None
    """

    labels = district_correlations.index.values

    plt.close()
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(labels)), district_correlations['correlation'].fillna(0).values, tick_label=labels, align='center')
    plt.xticks(rotation='vertical')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.suptitle(title)
    plt.show()


def print_correlation_report(conflict_data: pd.DataFrame, idp_data: pd.DataFrame, date_codes: list, districts: list,
                                            event_type: str = '', party: str = '',
                                            delta: bool = False, fatal: bool = False) -> None:
    """
    Takes a series of flags specifying a subset of movement and conflict data to analyze for correlation, and
    prints a report to STDOUT describing the data subset selected, overall correlation between the two variables,
    correlation by district (a subset of districts can be selected), and the names of districts which
    demonstrated positive correlation.

    :param conflict_data: a dataframe produced by clean_conflict_data
    :param idp_data: a dataframe produced by aggregate_idp_data
    :param date_codes: date codes for all months within the range of time being analyzed
    :param districts: a list of districts to produce calculate correlation statistics for
    :param event_type: selects a specific conflict event type to extract data for
    :param party: selects a specific party to extract data for
    :param delta:if True, calculates correlation for percent change in variables between months
    :param fatal: if True, counts number of fatalities instead of number of events
    :return: None
    """
    # General info
    time_range = f'{date_codes[0]} - {date_codes[-1]}'
    change = 'Yes' if delta else 'No'
    fatalities_or_counts = 'Fatalities' if fatal else 'Event Counts'
    group = party if party else 'All'
    event = event_type if event_type else 'All'

    # Correlations
    corr_deltas = calculate_conflict_movement_correlation(conflict_data, idp_data, date_codes,
                                                          delta=delta, event_type=event_type, party=party,
                                                          fatal=fatal).loc['conflict']['movement']

    corr_bar = district_wise_correlations(districts, conflict_data, idp_data, date_codes,
                                          delta=delta, event_type=event_type, party=party, fatal=fatal)

    positive_corr_bar = corr_bar.query('correlation > 0')

    print('\n----------- CONFLICT/MOVEMENT CORRELATION REPORT -----------')
    print(f'Time Range: {time_range}')
    print(f'Deltas: {change}')
    print('\n## Conflict Variable Details ##')
    print(f'\nCounts/Fatalities: {fatalities_or_counts}')
    print(f'Party: {group}')
    print(f'Event Type: {event}')
    print(f'\n## Correlation ##')
    print(f'\nOverall Correlation: {round(corr_deltas, 4)}')
    print(f'\nCorrelations by District:')
    for district in corr_bar.index.values:
        print(f'\t{district}: {corr_bar.loc[district]["correlation"]}')
    print(f'\nDistricts with Positive Correlations:')
    for district in positive_corr_bar.index.values:
        print(f'\t{district}')


def main() -> None:
    """
    A demonstration of this module's functionality. Tests three simple hypotheses:

    1. Change in the number of acts of political violence within an administrative division is at least moderately
    positively correlated with change in the number of IDP movements within and out of that division.

    2. Change in the number of acts of political violence involving non-combatants has a stronger positive correlation
    with change in the number of IDP movements compared with change in the number of acts overall.

    3. Change in the number of fatalities is at least moderately positively
    correlated with change in the number of IDP movements."

    Where:

    - |r| < 0.1 -> Minimal
    - 0.1 <= |r| < 0.3 -> Low
    - 0.3 <= |r| < 0.7 -> Moderate
    - 0.7 < |r| -> Strong

    :return: None
    """

    date_codes = ['2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6', '2019-7', '2019-8', '2019-9', '2019-10',
                  '2019-11', '2019-12', '2020-1', '2020-2']

    districts = ["Aleppo", "Al-Hasakeh", "Ar-Raqqa", "As-Sweida", "Damascus", "Dar'a", "Deir-ez-Zor",
                 "Hama", "Homs", "Idleb", "Lattakia", "Quneitra", "Rural Damascus", "Tartous"]

    conflict_data_path = 'data/conflict_data_syr.csv'

    idp_data_paths = ['data/01_idp_jan_19.xlsx', 'data/02_idp_feb_19.xlsm', 'data/03_idp_mar_19.xlsm',
                      'data/04_idp_apr_19.xlsm', 'data/05_idp_may_19.xlsm', 'data/06_idp_jun_19.xlsm',
                      'data/07_idp_jul_19.xlsm', 'data/08_idp_aug_19.xlsx', 'data/09_idp_sep_19.xlsx',
                      'data/10_idp_oct_19.xlsx', 'data/11_idp_nov_19.xlsx', 'data/12_idp_dec_19.xlsx',
                      'data/13_idp_jan_20.xlsx', 'data/14_idp_feb_20.xlsx']

    conflict_data = clean_conflict_data(conflict_data_path)

    idp_data = aggregate_idp_data(idp_data_paths, date_codes, districts)

    print_correlation_report(conflict_data, idp_data, date_codes, districts, delta=True)
    print_correlation_report(conflict_data, idp_data, date_codes, districts, delta=True, party='Civilians')
    print_correlation_report(conflict_data, idp_data, date_codes, districts, delta=True, fatal=True)


if __name__ == '__main__':
    main()


