import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from datetime import datetime
from scipy.optimize import fsolve
from scipy.optimize import curve_fit


class Measurement:
    def __init__(self, datetime_start, datetime_end, foldername):
        self.folder_path = '../'+foldername+'/'
        self.start_time =  datetime(year = datetime_start[0], month = datetime_start[1], 
                                    day = datetime_start[2], hour = datetime_start[3], 
                                    minute = datetime_start[4], second=datetime_end[5])
        self.end_time =  datetime(year = datetime_end[0], month = datetime_end[1], 
                                    day = datetime_end[2], hour = datetime_end[3], 
                                    minute = datetime_end[4], second=datetime_end[5])
        self.TRScans = []
        self.ZZplots = []
        self.currents_ZZ = []
        for file in os.listdir(self.folder_path):
            if file.endswith('.csv'):
                file_path = os.path.join(self.folder_path, file)
                
                pattern = r"DateTimeKeyStart_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_DateTimeKeyEnd"
                match_name_date = re.search(pattern, file)
                if match_name_date:
                    datetime_str = match_name_date.group(1)
                    creation_time = datetime.strptime(datetime_str, "%Y_%m_%d_%H_%M_%S")
                else:
                    creation_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    formatted_timestring = creation_time.strftime("%Y_%m_%d_%H_%M_%S")
                    os.rename(file_path, os.path.join(self.folder_path, f"DateTimeKeyStart_{formatted_timestring}_DateTimeKeyEnd{file}"))
                
        for file in os.listdir(self.folder_path):
            if file.endswith('.csv'):
                file_path = os.path.join(self.folder_path, file)
                pattern = r"DateTimeKeyStart_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_DateTimeKeyEnd"
                match_name_date = re.search(pattern, file)
                if match_name_date:
                    datetime_str = match_name_date.group(1)
                    creation_time = datetime.strptime(datetime_str, "%Y_%m_%d_%H_%M_%S")
                if creation_time > self.start_time and creation_time < self.end_time:
                    if 'TRScan' in file and '_CP_' in file:
                        self.TRScans.append(pd.read_csv(file_path, names = ['time', 'potential', 'current']))
                    if "EIS" in file and file.endswith("Acm2.csv"):
                        self.ZZplots.append(pd.read_csv(file_path, names = ['1', '2', '3']))
                        self.ZZplots[-1]['2'] *= -1
                        match1 = re.search(r'EIS (\d+(\.\d+)?)A', file)
                        match2 = re.search(r'EIS(\d+(\.\d+)?)A', file)
                        match3 = re.search(r'_(\d+(\.\d+)?)A', file)
                        if match1:
                            value = match1.group(1)
                            self.currents_ZZ.append(value)
                        if match2:
                            value = match2.group(1)
                            self.currents_ZZ.append(value)
                        if match3:
                            value = match3.group(1)
                            self.currents_ZZ.append(value)
            self.vs = []
            self.js = []
            for trscan in self.TRScans:
                J = np.mean(trscan['current'][-50:])
                V = np.mean(trscan['potential'][-50:])
                self.js.append(J)
                self.vs.append(V)
            self.js = np.array(self.js)
            self.vs = np.array(self.vs)
            
            
            self.rs = []
            
            for zzplot in self.ZZplots:
                for i in range(zzplot['1'].size-1):
                    if zzplot['2'][i]*zzplot['2'][i+1] < 0:
                        pol = np.polyfit([zzplot['1'][i], zzplot['1'][i+1]], [zzplot['2'][i],zzplot['2'][i+1]], 1)
                        res = fsolve(lambda x: np.polyval(pol, x), [0])[0]
                        res = max(res, 0)
                        self.rs.append(res)
                        break
            self.rs = np.array(self.rs)
        