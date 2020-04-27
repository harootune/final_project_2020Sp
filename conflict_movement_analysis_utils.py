import pandas as pd
import matplotlib.pyplot as plt


def extract_conflict_data(conflict_data: pd.DataFrame, date_codes: list, admin_district: str, event_type: str,
                          party: str, fatal: bool = False) -> pd.DataFrame:
    """

    :param conflict_data:
    :param date_codes:
    :param admin_district:
    :param event_type:
    :param party:
    :param fatal:
    :return:
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

    :param idp_data:
    :param admin_district:
    :return:
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

    :param conflict_data:
    :param idp_data:
    :param date_codes:
    :param event_type:
    :param admin_district:
    :param party:
    :param delta:
    :param fatal:
    :return:
    """
    extracted_conflict_data = extract_conflict_data(conflict_data, date_codes,
                                                    admin_district, event_type, party, fatal=fatal)
    extracted_idp_data = extract_idp_data(idp_data, admin_district)
    corr_frame = extracted_conflict_data.join(extracted_idp_data)
    if delta:
        corr_frame = corr_frame.pct_change()
        corr_frame = corr_frame.drop(labels='2019-1')

    labels = {'iso': 'conflict', 'Grand Total': 'movement'}  # TODO: check if this is even working
    corr_frame = corr_frame.corr().rename(columns=labels, index=labels)

    return corr_frame


def district_wise_correlations(districts: list, conflict_data: pd.DataFrame, idp_data: pd.DataFrame, date_codes: list,
                               event_type: str = '', party: str = '', delta: bool = False, fatal: bool = False) -> pd.DataFrame:
    """

    :param districts:
    :param conflict_data:
    :param idp_data:
    :param date_codes:
    :param event_type:
    :param party:
    :param delta:
    :param fatal:
    :return:
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

    :param district_correlations:
    :param title:
    :param x_label:
    :param y_label:
    :return:
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