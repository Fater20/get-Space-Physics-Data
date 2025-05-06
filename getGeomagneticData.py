import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
from tqdm import tqdm

from datetime import datetime, timedelta
import calendar

def getDstData(time):
    '''
    获取指定时间的Dst数据
    时间分辨率为1小时
    :param time: str, 时间格式为YYYY-MM
    :return: DataFrame, 包含时间和Dst数据
    '''
    datetime_object = datetime.strptime(time, '%Y-%m')
    year = datetime_object.year
    month = datetime_object.month
    # year = time[0:4]
    # month = time[5:7]
    # 发送HTTP请求获取网页内容
    # 1957-2020:        https://wdc.kugi.kyoto-u.ac.jp/dst_final/index.html
    # 2021-2024.10 :    https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/index.html
    # 2024.10- :        https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/index.html
    if year < 2021:
        url = "https://wdc.kugi.kyoto-u.ac.jp/dst_final/"+str(year)+str(month).zfill(2)+"/index.html"
    elif datetime_object < datetime(2024, 10, 1):
        url = "https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/"+str(year)+str(month).zfill(2)+"/index.html"
    else:
        url = "https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/"+str(year)+str(month).zfill(2)+"/index.html"


    #url = "https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/"+str(year)+str(month).zfill(2)+"/index.html"

    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")
    html_content = response.text

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # 找到dst数据部分
    table = soup.find_all('pre')

    table = np.array(table[0].text.split('\n'))

    # 清除无用部分
    all_index = np.where(table != '')
    table = table[all_index]
    start_index = np.where(table == 'DAY')

    # 提取数据
    data = []
    for row in table[start_index[0][0]+1:]:
        day_data = []
        row_data = row.split(' ')
        for hours_data in row_data:
            if hours_data != '':
                if len(hours_data)>3:
                    for j in range(int(len(hours_data)/4)+1):
                        if j == 0:
                            if hours_data[0:len(hours_data)%4] != '':
                                day_data.append(hours_data[0:len(hours_data)%4])
                        else:
                            day_data.append(hours_data[len(hours_data)%4+(j-1)*4:len(hours_data)%4+j*4])
                else:
                    day_data.append(hours_data)
        data.append(day_data)
    data = np.array(data)

    # data_df = pd.DataFrame(data, columns=['day', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'])
    df_temp = []
    for i in range(len(data)):
        for j in range(24):
            timestamp = str(year)+'-'+str(month).zfill(2)+'-'+str(int(data[i][0])).zfill(2)+' '+str(j).zfill(2)+':00:00'
            dst = int(data[i][j+1])
            df_temp.append([timestamp, dst])
    df = pd.DataFrame(df_temp, columns=['Time', 'Dst'])
    df.Time = pd.to_datetime(df.Time)
    # df_temp.to_csv(f"Dstindex_{time}.csv", index=False)
    return df
    # data_df.to_csv('input/dst_data/'+str(year)+str(month).zfill(2)+'_dst.csv', index=False)


def getRealtimeAEData(time):
    '''
    获取指定时间的AE数据
    时间分辨率为1分钟
    :param time: str, 时间格式为YYYY-MM
    :return: DataFrame, 包含时间和AE数据
    '''
    index_list = ["AE", "AL", "AU", "AO"]
    df = pd.DataFrame()
    for i, index_name in enumerate(index_list):
        url = "https://wdc.kugi.kyoto-u.ac.jp/ae_realtime/data_dir/"
        records = []
        for day in tqdm(range(1, calendar.monthrange(time.year, time.month)[1] + 1)):
            url_index = url + f"{time.year}/{str(time.month).zfill(2)}/{str(day).zfill(2)}/{index_name.lower()}{str(time.year%100).zfill(2)}{str(time.month).zfill(2)}{str(day).zfill(2)}"
            response_index = requests.get(url_index)
            if response_index.status_code != 200:
                raise Exception(f"请求失败，状态码：{response_index.status_code}")
            text_index = response_index.text

            for line in text_index.strip().splitlines():
                time_str = line[12:21]
                values_str = line[34:394].strip().split()
                
                base_time = datetime(int("20" + time_str[0:2]), int(time_str[2:4]), int(time_str[4:6]), int(time_str[7:9]))
                for i, val in enumerate(values_str):
                    timestamp = base_time + timedelta(minutes=i)
                    records.append([timestamp, int(val)])
        df_tmp = pd.DataFrame(records, columns=['Time', index_name])
        df = pd.merge(df, df_tmp, on='Time', how='outer') if not df.empty else df_tmp
    
    return df

# time format: YYYY-MM
def getProvisionalAEData(time):
    '''
    获取指定时间的AE数据
    时间分辨率为1分钟
    :param time: str, 时间格式为YYYY-MM
    :return: DataFrame, 包含时间和AE数据
    '''
    Tens = str(int(time.year / 10))
    Year = str(int(time.year % 10))
    Month = str(time.month).zfill(2)

    # url = "https://wdc.kugi.kyoto-u.ac.jp/cgi-bin/aeasy-cgi?\
    #     Tens=200&Year=0&Month=01&Day_Tens=0&Days=0&Hour=00&min=00\
    #     &Dur_Day_Tens=00&Dur_Day=2&Dur_Hour=00&Dur_Min=00\
    #     &Image+Type=GIF&COLOR=COLOR&AE+Sensitivity=0&ASY%2FSYM++Sensitivity=0&Output=AE&Out+format=WDC"
    # 为简化，请求的时间范围均为31天，获取31天的数据后再进行时间段筛选
    url = "https://wdc.kugi.kyoto-u.ac.jp/cgi-bin/aeasy-cgi?"
    url += f"Tens={Tens}&Year={Year}&Month={Month}&Day_Tens=00&Days=0&Hour=00&min=00"
    url += f"&Dur_Day_Tens=03&Dur_Day=1&Dur_Hour=00&Dur_Min=00"
    url += "&Image+Type=GIF&COLOR=COLOR&AE+Sensitivity=0&ASY%2FSYM++Sensitivity=0&Output=AE&Out+format=WDC"
    print(url)
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")
    text = response.text
    AE_records = []
    AL_records = []
    AU_records = []
    AO_records = []
    df = pd.DataFrame()
    for line in text.strip().splitlines():
        time_str = line[12:21]
        values_str = line[34:394].strip().split()
        index_name = line[21:24].strip()
        base_time = datetime(int("20" + time_str[0:2]), int(time_str[2:4]), int(time_str[4:6]), int(time_str[7:9]))
        for i, val in enumerate(values_str):
            timestamp = base_time + timedelta(minutes=i)
            # records.append([timestamp, int(val)])
            if index_name == "AE":
                AE_records.append([timestamp, int(val)])
            elif index_name == "AL":
                AL_records.append([timestamp, int(val)])
            elif index_name == "AU":
                AU_records.append([timestamp, int(val)])
            elif index_name == "AO":
                AO_records.append([timestamp, int(val)])
                
    AE_df = pd.DataFrame(AE_records, columns=['Time', 'AE'])
    AL_df = pd.DataFrame(AL_records, columns=['Time', 'AL'])
    AU_df = pd.DataFrame(AU_records, columns=['Time', 'AU'])
    AO_df = pd.DataFrame(AO_records, columns=['Time', 'AO'])
    df = pd.merge(AE_df, AL_df, on='Time', how='outer')
    df = pd.merge(df, AU_df, on='Time', how='outer')
    df = pd.merge(df, AO_df, on='Time', how='outer')
    df.Time = pd.to_datetime(df.Time)
    # drop the rows not in the range of YYYY-MM
    start_time = datetime(int(Tens+Year), int(Month), 1)
    if int(Month) == 12:
        end_time = datetime(int(Tens+Year)+1, 1, 1)
    else:
        end_time = datetime(int(Tens+Year), int(Month)+1, 1)

    df = df[(df['Time'] >= start_time) & (df['Time'] < end_time)]
    # df = pd.DataFrame(AL_records, columns=['Time', 'AL'])
    # df = pd.DataFrame(AU_records, columns=['Time', 'AU'])
    # df = pd.DataFrame(AO_records, columns=['Time', 'AO'])
        # df = pd.DataFrame(records, columns=['Time', index_name])
    # df.to_csv(f"AEindex_{time}.csv", index=False)
    return df

def getAEData(time):
    '''
    获取指定时间的AE数据
    时间分辨率为1分钟
    :param time: str, 时间格式为YYYY-MM
    :return: DataFrame, 包含时间和AE数据
    '''
    datetime_object = datetime.strptime(time, '%Y-%m')
    year = datetime_object.year
    month = datetime_object.month

    if year < 2020:
        df = getProvisionalAEData(datetime_object)
    else:
        df = getRealtimeAEData(datetime_object)
    
    return df

def getKpapData(time):
    '''
    获取指定时间的Kp数据
    时间分辨率为3小时
    :param time: str, 时间格式为YYYY-MM
    :return: DataFrame, 包含时间和Kp, ap数据
    '''
    url = "https://kp.gfz.de/app/files/Kp_ap_since_1932.txt"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码：{response.status_code}")
    text = response.text
    # 跳过第一个字符为'#'的行
    lines = text.split('\n')
    lines = [line for line in lines if not line.startswith('#')]
    # start time: 1932-01-01 00:00:00
    start_time = datetime(1932, 1, 1, 0, 0, 0)
    find_time = datetime.strptime(time, '%Y-%m')
    # estimate the line number of the find time
    # 1 line = 3 hours
    # 1 day = 24 hours
    # 1 month = 30 days
    # 1 year = 365 days
    # 1 month = 30 days = 30 * 24 hours = 720 hours
    # 1 year = 365 days = 365 * 24 hours = 8760 hours
    # 1 month = 30 days = 30 * 24 / 3 lines = 240 lines
    # 1 year = 365 days = 365 * 24 / 3 lines = 2920 lines
    findtime_startindex = int((find_time - start_time).total_seconds() / 3 / 3600)
    month_days = calendar.monthrange(find_time.year, find_time.month)[1]
    findtime_endindex = int((find_time + timedelta(days=month_days) - start_time).total_seconds() / 3 / 3600)
    # 读取数据
    # The format for each line is (i stands for integer, f for float):
    #iiii ii ii ff.f ff.ff fffff.fffff fffff.fffff ff.fff iiii i
    # The parameters in each line are:
    #YYYY MM DD hh.h hh._m        days      days_m     Kp   ap D
    #2023 12 01 00.0 01.50 33572.00000 33572.06250  4.333   32 2
    records = []
    for line in lines[findtime_startindex:findtime_endindex]:
        # 解析数据
        year = int(line[0:4])
        month = int(line[5:7])
        day = int(line[8:10])
        hour = int(line[11:13])
        Kp = float(line[46:52])
        ap = int(line[53:57])
        D = int(line[58:59])
        # 计算时间
        timestamp = datetime(year, month, day, hour)
        records.append([timestamp, Kp, ap, D])
    # 转换为DataFrame
    df = pd.DataFrame(records, columns=['Time', 'Kp', 'ap', 'D'])
    # 将时间戳转换为datetime格式
    df['Time'] = pd.to_datetime(df['Time'])
    return df
    


def getGeomagneticData(time, index_type='Dst'):
    '''
    获取指定时间的Dst和AE数据
    :param time: str, 时间格式为YYYY-MM
    :param index_type: str or list, 指定获取的指数类型，'Dst'或'AE'，默认'Dst'
    :return: DataFrame, 包含时间和指数数据
    '''

    if isinstance(index_type, str):
        index_type = [index_type]  # 如果是字符串，转成列表
    
    df = pd.DataFrame()
    for idx in index_type:
        if idx == 'Dst':
            df_tmp = getDstData(time)
        elif idx == 'AE':
            df_tmp = getAEData(time)
        elif idx == 'Kpap':
            df_tmp = getKpapData(time)
        else:
            raise ValueError(f"Index Type '{idx}' not supported.")
        # 合并数据
        if df.empty:
            df = df_tmp
        else:
            df = pd.merge(df, df_tmp, on='Time', how='outer')
    
    return df


if __name__ == "__main__":
    # Geomagnetic Data Service(https://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html)
    # If there is no data for the time period you entered or a request error occurs, 
    # first check the description of the data time range on the website.
    time = '2023-12'
    Index_df = getGeomagneticData(time, index_type='Kpap')
    Index_df.to_csv(f"Index_{time}.csv", index=False)