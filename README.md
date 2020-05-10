### Conflict and Movement in Syria, 2019-2020
#### UIUC, iSchool, IS590PR, Spring 2020, Final Project
By Derek Harootune Otis

---

#### Introduction

This project analyzes the movement of internally displaced persons within Syria in relation to the ebb and flow of Syria's ongoing civil war. It evaluates changes in three conflict-related variables in relation to changes in IDP movement, hoping to identify candidate features for future predictive modeling of IDP movement in the region. Additionally, it examines how the relationship between these variables and IDP movement differs across Syria's governorates.

#### Running the Project

A version of the notebook with a recently-executed kernel is included in the repository.

*Running Locally*:
1. Clone the repository where desired
2. Unzip "UNZIP_ME_data_files.zip" \(located in final_project_2020Sp/data\), outputting to the same directory the file is located in
3. Open "conflict_and_movement_in_syria_2019-2020.ipynb" using your desired Jupyter Notebook viewer
4. Reset the notebook's kernel and rerun in sequence

Running "conflict_movement_analysis_utils.py" as \__main\__ will also produce a small demonstration testing the same hypotheses as the notebook

#### Hypotheses

1. Change in the number conflict events is at least moderately positively correlated with change in the number of IDP movements at the national level.

2. Change in the number of conflict events involving non-combatants has a more strongly positive correlation with change in the number of IDP movements compared with change in the number of conflict events overall, at the national level.

3. Change in the number of fatalities is at least moderately positively correlated with change in the number of IDP movements at the national level.

#### Results & Conclusions Summary

None of these hypotheses as written were supported.  
    
However, an interesting coincidence emerged - all three conflict-related variables analyzed in relation to change in IDP movement demonstrated positive correlation with change in movement specifically in the Northern governorates of Syria, during this time period.  
    
Further discussion of this coincidence and its potential implications can be seen in "conflict_and_movement_in_syria_2019-2020.ipynb"