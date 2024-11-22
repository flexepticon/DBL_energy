import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from datetime import datetime
from scipy.optimize import fsolve
from scipy.optimize import curve_fit


import os
import re
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import fsolve

class Measurement:
    """
    A class to process experimental data files within a specific folder and timeframe. 
    Extracts and processes data to compute key parameters such as VAC curves, JR curves, 
    and overpotentials.
    
    Attributes:
        folder_path (str): Path to the data folder.
        start_time (datetime): Start of the timeframe for processing files.
        end_time (datetime): End of the timeframe for processing files.
        TRScans (list): List of TR scan DataFrames.
        ZZplots (list): List of EIS DataFrames.
        currents_ZZ (list): List of currents for ZZ plots.
        currents_TR (list): List of currents for TR scans.
        missing (list): List of files where currents couldn't be extracted.
        VAC_dataframe (pd.DataFrame): Processed Volt-Amper curve data.
        JR_dataframe (pd.DataFrame): Processed Current Density-Resistance curve data.
        for_computation (pd.DataFrame): DataFrame for overpotential computation.
        overpotential (list): List of computed overpotentials.
        slope (float): Slope of the Tafel plot
    """

    def __init__(self, datetime_start, datetime_end, foldername):
        """
        Initializes the Measurement object, processes files, and computes results.
        
        Args:
            datetime_start (list): Start datetime as [year, month, day, hour, minute, second].
            datetime_end (list): End datetime as [year, month, day, hour, minute, second].
            foldername (str): Name of the folder containing experimental data.
        """
        # Define folder path
        self.folder_path = '../' + foldername + '/'
        self.missing_files = False
        # Define start and end times
        self.start_time = datetime(year=datetime_start[0], month=datetime_start[1], 
                                    day=datetime_start[2], hour=datetime_start[3], 
                                    minute=datetime_start[4], second=datetime_start[5])
        self.end_time = datetime(year=datetime_end[0], month=datetime_end[1], 
                                  day=datetime_end[2], hour=datetime_end[3], 
                                  minute=datetime_end[4], second=datetime_end[5])

        # Initialize attributes
        self.TRScans = []       # List of TR scan DataFrames
        self.ZZplots = []       # List of ZZ plot DataFrames
        self.currents_ZZ = []   # List of currents for ZZ plots
        self.currents_TR = []   # List of currents for TR scans
        self.missing = []       # List of files with missing current data

        # Process all files in the folder
        for file in os.listdir(self.folder_path):
            if file.endswith('.csv'):
                file_path = os.path.join(self.folder_path, file)

                # Check for datetime in filename, if missing rename with creation time
                pattern = r"DateTimeKeyStart_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_DateTimeKeyEnd"
                match_name_date = re.search(pattern, file)
                if match_name_date:
                    datetime_str = match_name_date.group(1)
                    creation_time = datetime.strptime(datetime_str, "%Y_%m_%d_%H_%M_%S")
                else:
                    # Use file creation time if datetime missing
                    creation_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    formatted_timestring = creation_time.strftime("%Y_%m_%d_%H_%M_%S")
                    os.rename(file_path, os.path.join(self.folder_path, f"DateTimeKeyStart_{formatted_timestring}_DateTimeKeyEnd{file}"))
        
        # Re-process files with new names
        for file in os.listdir(self.folder_path):
            if file.endswith('.csv'):
                file_path = os.path.join(self.folder_path, file)
                pattern = r"DateTimeKeyStart_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})_DateTimeKeyEnd"
                match_name_date = re.search(pattern, file)
                if match_name_date:
                    datetime_str = match_name_date.group(1)
                    creation_time = datetime.strptime(datetime_str, "%Y_%m_%d_%H_%M_%S")
                
                # Process files within the given timeframe
                if creation_time > self.start_time and creation_time < self.end_time:
                    # Process TRScan files
                    if 'TRScan' in file and 'CP' in file:
                        self.TRScans.append(pd.read_csv(file_path, names=['time', 'V', 'I']))

                        # Extract current from filename using regex
                        TR_match1 = re.search(r' (\d+(\.\d+)?)A', file)
                        TR_match2 = re.search(r'_(\d+(\.\.\d+)?)A', file)
                        TR_match3 = re.search(r'_(\d+(\.\d+)?)A', file)
                        TR_match4 = re.search(r' (\d+(\.\d+)?) A', file)

                        if TR_match1:
                            value = TR_match1.group(1)
                            self.currents_TR.append(float(value))
                        elif TR_match2:
                            value = TR_match2.group(1).replace('..', '.')
                            self.currents_TR.append(float(value))
                        elif TR_match3:
                            value = TR_match3.group(1)
                            self.currents_TR.append(float(value))
                        elif TR_match4:
                            value = TR_match4.group(1)
                            self.currents_TR.append(float(value))
                        else:
                            self.missing_files = True
                            self.missing.append(file)

                    # Process EIS files
                    if "EIS" in file and file.endswith("Acm2.csv"):
                        self.ZZplots.append(pd.read_csv(file_path, names=['Zr', 'Zi', '3']))
                        self.ZZplots[-1]['Zi'] *= -1  # Invert imaginary part for proper plotting

                        # Extract current from filename using regex
                        match1 = re.search(r'EIS (\d+(\.\d+)?)A', file)
                        match2 = re.search(r'EIS(\d+(\.\d+)?)A', file)
                        match3 = re.search(r'_(\d+(\.\d+)?)A', file)

                        if match1:
                            value = match1.group(1)
                            self.currents_ZZ.append(float(value))
                        elif match2:
                            value = match2.group(1)
                            self.currents_ZZ.append(float(value))
                        elif match3:
                            value = match3.group(1)
                            self.currents_ZZ.append(float(value))
                        else:
                            self.missing.append(file)
        
        if self.missing_files:
            print('Files cannot be processed:')
            print(self.missing)
        else:
            # Process TR scans for VAC curves
            self.vs = []  # List of mean voltages
            self.js = []  # List of mean currents
            for trscan in self.TRScans:
                J = np.mean(trscan['I'][-50:])  # Mean current of last 50 points
                V = np.mean(trscan['V'][-50:])  # Mean voltage of last 50 points
                self.js.append(J)
                self.vs.append(V)

            self.js = np.array(self.js)
            self.vs = np.array(self.vs)

            # Process ZZ plots for resistance values
            self.rs = []  # List of resistances
            for zzplot in self.ZZplots:
                for i in range(zzplot['Zr'].size - 1):
                    # Find zero crossing of Zi to compute resistance
                    if zzplot['Zi'][i] * zzplot['Zi'][i + 1] < 0:
                        pol = np.polyfit([zzplot['Zr'][i], zzplot['Zr'][i + 1]], [zzplot['Zi'][i], zzplot['Zi'][i + 1]], 1)
                        res = fsolve(lambda x: np.polyval(pol, x), [0])[0]
                        res = max(res, 1e-10)  # Ensure resistance is non-negative
                        self.rs.append(res)
                        break
            self.rs = np.array(self.rs)

            # Create VAC DataFrame and group by current
            self.VAC_dataframe = pd.DataFrame({'V': self.vs, 'J': self.currents_TR})
            self.VAC_dataframe = self.VAC_dataframe.groupby('J', as_index=False)['V'].mean()

            # Create JR DataFrame and group by current
            self.JR_dataframe = pd.DataFrame({'R': self.rs, 'J': self.currents_ZZ})
            self.JR_dataframe = self.JR_dataframe.groupby('J', as_index=False)['R'].mean()

            # Merge VAC and JR data and compute overpotential
            self.for_computation = pd.DataFrame({
                'V': self.VAC_dataframe['V'],
                'J VAC': self.VAC_dataframe['J'],
                'R': self.JR_dataframe['R'],
                'J JR': self.JR_dataframe['J']
            })
            self.for_computation = self.for_computation[self.for_computation['J VAC'] == self.for_computation['J JR']]
            self.for_computation['Overpotential'] = self.for_computation['V'] - 4 * self.for_computation['J JR'] * self.for_computation['R'] - 1.23

            # Store overpotential values and slope of log(current) vs overpotential
            self.overpotential = list(self.for_computation['Overpotential'])
            self.slope = np.polyfit(np.log10(self.for_computation['J JR']), self.for_computation['Overpotential'], 1)[0]
