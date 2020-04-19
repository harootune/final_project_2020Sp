import pandas as pd
from pathlib import Path

# constants

months = ['Jan_19', 'Feb_19', 'Mar_19', 'Apr_19', 'May_19', 'Jun_19', 'Jul_19', 'Aug_19', 'Sep_19', 'Oct_19',
                    'Nov_19', 'Dec_19', 'Jan_20', 'Feb_20']

# prepare conflict data

conflict_data_path = Path('data/conflict_data_syr.csv')
conflict_data = pd.read_csv(conflict_data_path, index_col='data_id')

conflict_data['event_date'] = pd.to_datetime(conflict_data['event_date'])

conflict_data['month'] = conflict_data.apply(lambda row: row['event_date'].month, axis=1)

conflict_data = conflict_data.groupby(['year', 'month', 'admin1']).count()

# administrative_zones = list({admin for admin in conflict_data.index['admin1']})
#
# print(administrative_zones)

print(conflict_data.index) # TODO: Deal with this multi-index

new_conflict_data = pd.DataFrame()

print(conflict_data['event_id_cnty'])




# prepare idp data

idp_data_paths = ['data/01_idp_jan_19.xlsx', 'data/02_idp_feb_19.xlsm', 'data/03_idp_mar_19.xlsm',
                  'data/04_idp_apr_19.xlsm', 'data/05_idp_may_19.xlsm', 'data/06_idp_jun_19.xlsm',
                  'data/07_idp_jul_19.xlsm', 'data/08_idp_aug_19.xlsx', 'data/09_idp_sep_19.xlsx',
                  'data/10_idp_oct_19.xlsx', 'data/11_idp_nov_19.xlsx', 'data/12_idp_dec_19.xlsx',
                  'data/13_idp_jan_20.xlsx', 'data/14_idp_feb_20.xlsx']
idp_data = pd.DataFrame(index=["Aleppo", "Al-Hasakeh", "Ar-Raqqa", "As-Sweida", "Damascus", "Dar'a", "Deir-ez-Zor",
                               "Hama", "Homs", "Idleb", "Lattakia", "Quneitra", "Rural Damascus", "Tartous", "Unknown",
                               "Grand Total"])

for i in range(len(idp_data_paths)):
    path = idp_data_paths[i]
    month_data = pd.read_excel(path, sheet_name='Table-Origin_vs_Departure', index_col='Origin')["Grand Total"]
    idp_data = idp_data.join(month_data, rsuffix=str(i))

idp_data.columns = months

# idp_data status: total movement from origin per month + grand total for all regions per month

