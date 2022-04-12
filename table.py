import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(13,15))

data = [np.unique(range(0, 6)),
        np.unique(range(0, 6)),
        np.unique(range(0, 6))]
        
rows = ["Active/Passive", "Active/Denial", "Passive/Denial"] 
    
columns = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
the_table = plt.table(cellText=data,
                      rowLabels=rows,
                      colLabels=columns,
                      loc='bottom',
                      bbox = [.2, 0.4, 0.8, 0.2])
                          
fig.savefig('table.png')