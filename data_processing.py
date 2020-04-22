import pandas as pd
from pathlib import Path

# constants

MONTHS = ['2019-1', '2019-2', '2019-3', '2019-4', '2019-5', '2019-6', '2019-7', '2019-8', '2019-9', '2019-10',
                    '2019-11', '2019-12', '2020-1', '2020-2']

DISTRICTS = ["Aleppo", "Al-Hasakeh", "Ar-Raqqa", "As-Sweida", "Damascus", "Dar'a", "Deir-ez-Zor",
                               "Hama", "Homs", "Idleb", "Lattakia", "Quneitra", "Rural Damascus", "Tartous"]




# prepare conflict data
conflict_data_path = Path('data/conflict_data_syr.csv')
conflict_data = pd.read_csv(conflict_data_path, index_col='data_id')

# Date processing
conflict_data['event_date'] = pd.to_datetime(conflict_data['event_date'])
conflict_data['month'] = conflict_data.apply(lambda row: row['event_date'].month, axis=1)
conflict_data['month'] = conflict_data['month'].astype(str)
conflict_data['year'] = conflict_data['year'].astype(str)
conflict_data['date_code'] = conflict_data['year'] + '-' + conflict_data['month']

# Counts by division and event
event_data = conflict_data.groupby(['admin1', 'event_type', 'date_code']).count()

# Counts by division only
admin_data = conflict_data.groupby(['admin1', 'date_code']).count()['iso']
admin_data = admin_data.reset_index(1)
admin_data = admin_data.pivot(columns='date_code', values='iso')[MONTHS]
admin_data.loc['Grand Total'] = admin_data.sum()

print(admin_data)

# admin data status: total  from origin per month + grand total for all regions per month




# prepare idp data
idp_data_paths = ['data/01_idp_jan_19.xlsx', 'data/02_idp_feb_19.xlsm', 'data/03_idp_mar_19.xlsm',
                  'data/04_idp_apr_19.xlsm', 'data/05_idp_may_19.xlsm', 'data/06_idp_jun_19.xlsm',
                  'data/07_idp_jul_19.xlsm', 'data/08_idp_aug_19.xlsx', 'data/09_idp_sep_19.xlsx',
                  'data/10_idp_oct_19.xlsx', 'data/11_idp_nov_19.xlsx', 'data/12_idp_dec_19.xlsx',
                  'data/13_idp_jan_20.xlsx', 'data/14_idp_feb_20.xlsx']
idp_data = pd.DataFrame(index=DISTRICTS+["Unknown", "Grand Total"])

for i in range(len(idp_data_paths)):
    path = idp_data_paths[i]
    month_data = pd.read_excel(path, sheet_name='Table-Origin_vs_Departure', index_col='Origin')["Grand Total"]
    idp_data = idp_data.join(month_data, rsuffix=str(i))

# re-label columns and drop unknown
idp_data = idp_data.drop(labels='Unknown')
idp_data.columns = MONTHS

print(idp_data)

# idp_data status: total movement from origin per month + grand total for all regions per month

