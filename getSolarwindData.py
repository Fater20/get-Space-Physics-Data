import requests

import pandas as pd
import numpy as np
from io import StringIO
import calendar
from datetime import datetime

from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")



# get ACE Data
def getACEdata_1h(year, month):
    # https://sohoftp.nascom.nasa.gov/sdb/goes/ace/monthly/202405_ace_swepam_1h.txt
    url1 = "https://sohoftp.nascom.nasa.gov/sdb/goes/ace/monthly/"+str(year)+str(month).zfill(2)+"_ace_swepam_1h.txt"
    # https://sohoftp.nascom.nasa.gov/sdb/goes/ace/monthly/202405_ace_mag_1h.txt
    url2 = "https://sohoftp.nascom.nasa.gov/sdb/goes/ace/monthly/"+str(year)+str(month).zfill(2)+"_ace_mag_1h.txt"

    response1 = requests.get(url1)
    response2 = requests.get(url2)

    text1 = response1.text
    text2 = response2.text

    df1 = pd.read_csv(StringIO(text1), lineterminator='\n', skiprows=range(0, 18), header=None, delim_whitespace=True)
    df2 = pd.read_csv(StringIO(text2), lineterminator='\n', skiprows=range(0, 20), header=None, delim_whitespace=True)
    #                Modified Seconds   -------------  Solar Wind  -----------
    # UT Date   Time  Julian  of the          Proton      Bulk         Ion
    # YR MO DA  HHMM    Day     Day     S    Density     Speed     Temperature
    #-------------------------------------------------------------------------
    df1.columns = ['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay', 'S1', 'ProtonDensity', 'BulkSpeed', 'IonTemperature']
    #                 Modified Seconds
    # UT Date   Time  Julian   of the   ----------------  GSM Coordinates ---------------
    # YR MO DA  HHMM    Day      Day    S     Bx      By      Bz      Bt     Lat.   Long.
    #------------------------------------------------------------------------------------
    df2.columns = ['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay', 'S2', 'Bx', 'By', 'Bz', 'Bt', 'Lat', 'Lng']
    
    df = pd.merge(df1, df2, on=['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay'])
    
    df["month"] = df["month"].astype(str).str.zfill(2)
    df["day"] = df["day"].astype(str).str.zfill(2)
    df["HHMM"] = df["HHMM"].astype(str).str.zfill(4)
    df["Time"] = pd.to_datetime(df[['year', 'month', 'day', 'HHMM']].astype(str).agg(''.join, axis=1), format='%Y%m%d%H%M')
    df = df.drop(columns=['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay'])
    df = df[['Time', 'S1','ProtonDensity', 'BulkSpeed', 'IonTemperature', 'S2', 'Bx', 'By', 'Bz', 'Bt', 'Lat', 'Lng']]
    
    return df

def getACEdata_1m(year, month, day):
    # https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/20010807_ace_swepam_1m.txt
    url1 = "https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/"+str(year)+str(month).zfill(2)+str(day).zfill(2)+"_ace_swepam_1m.txt"
    # https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/20010807_ace_mag_1m.txt
    url2 = "https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/"+str(year)+str(month).zfill(2)+str(day).zfill(2)+"_ace_mag_1m.txt"

    response1 = requests.get(url1)
    response2 = requests.get(url2)

    text1 = response1.text
    text2 = response2.text

    df1 = pd.read_csv(StringIO(text1), lineterminator='\n', skiprows=range(0, 18), header=None, delim_whitespace=True)
    df2 = pd.read_csv(StringIO(text2), lineterminator='\n', skiprows=range(0, 20), header=None, delim_whitespace=True)
    #                Modified Seconds   -------------  Solar Wind  -----------
    # UT Date   Time  Julian  of the          Proton      Bulk         Ion
    # YR MO DA  HHMM    Day     Day     S    Density     Speed     Temperature
    #-------------------------------------------------------------------------
    df1.columns = ['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay', 'S1', 'ProtonDensity', 'BulkSpeed', 'IonTemperature']
    #                 Modified Seconds
    # UT Date   Time  Julian   of the   ----------------  GSM Coordinates ---------------
    # YR MO DA  HHMM    Day      Day    S     Bx      By      Bz      Bt     Lat.   Long.
    #------------------------------------------------------------------------------------
    df2.columns = ['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay', 'S2', 'Bx', 'By', 'Bz', 'Bt', 'Lat', 'Lng']
    
    df = pd.merge(df1, df2, on=['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay'])
    
    df["month"] = df["month"].astype(str).str.zfill(2)
    df["day"] = df["day"].astype(str).str.zfill(2)
    df["HHMM"] = df["HHMM"].astype(str).str.zfill(4)
    df["Time"] = pd.to_datetime(df[['year', 'month', 'day', 'HHMM']].astype(str).agg(''.join, axis=1), format='%Y%m%d%H%M')
    df = df.drop(columns=['year', 'month', 'day', 'HHMM', 'ModifiedJulianDay', 'SecondsoftheDay'])
    df = df[['Time', 'S1','ProtonDensity', 'BulkSpeed', 'IonTemperature', 'S2', 'Bx', 'By', 'Bz', 'Bt', 'Lat', 'Lng']]
    
    return df

def getSolarwindData(time, mission='ACE', interval='1h'):
    """
    Get solar wind data from ACE spacecraft.
    
    Parameters:
    time (str): Time in the format 'YYYY-MM-DD HH:MM:SS'.
    start (str): Start time in the format 'YYYY-MM-DD HH:MM:SS'.
    end (str): End time in the format 'YYYY-MM-DD HH:MM:SS'.
    interval (str): Interval for data retrieval ('1h' or '1m'). Default is '1h'.
    
    Returns:
    pd.DataFrame: DataFrame containing solar wind data.
    """
    
    time = pd.to_datetime(time)
    year = time.year
    month = time.month
    if mission == 'ACE':
        if interval == '1h':
            df = getACEdata_1h(year, month)
        elif interval == '1m':
            df = pd.DataFrame()
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                # Get data for each day in the month
                try:
                    print(f"Retrieving data for {year}-{month:02d}-{day:02d}...")
                    df_day = getACEdata_1m(year, month, day)
                    df = pd.concat([df, df_day], ignore_index=True)
                except Exception as e:
                    print(f"Error retrieving data for {year}-{month:02d}-{day:02d}: {e}")
                    
            df.sort_values(by='Time', inplace=True)

        else:
            raise ValueError("Invalid interval. Use '1h' or '1m'.")
    else:
        raise ValueError("Invalid mission. Use 'ACE'.")

    
    return df

if __name__ == "__main__":
    time = "2023-12"
    mission = "ACE"
    interval = "1m"
    df = getSolarwindData(time, mission, interval)
    df.to_csv(f"{mission}_{time}_{interval}.csv", index=False)