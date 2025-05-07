# Space Physics Data Fetcher (Updated 2025.05.07)
本项目用于快速获取下载各类空间科学数据。


## ✨ 功能简介

### Geomagnetic Data 

该部分用于从日本京都大学地磁观测中心（WDC for Geomagnetism, Kyoto）自动获取 **Dst 指数** 和 **AE 指数** 数据，从亥姆霍兹德国地理研究中心（GFZ）自动获取 **Kp 指数** 和 **ap 指数** 数据。支持按月查询，输出为标准的 `DataFrame` 并可保存为 `.csv` 文件。(更多指数支持更新中...)

- **获取 Dst 指数**（1小时分辨率）
  - 根据年份自动选择最终版、临时版或实时版数据源。
- **获取 AE 指数（AE/AL/AU/AO）**（1分钟分辨率）
  - 根据年份选择实时数据或临时数据接口。
- **获取 Kp 和 ap指数** （3小时分辨率）
  - 根据查询时间寻找指定数据。
- **支持多种指数组合查询**
  - 可以通过传入列表一次性下载多种地磁指数。
- **统一输出格式**
  - 返回 `pandas.DataFrame` 格式，包含时间戳与对应指数值。

### Solar Wind Data

该部分用于从NASA提供的ftp链接中获取太阳风相关任务的数据。支持按月查询，支持指定任务和时间分辨率，输出为标准的 `DataFrame` 并可保存为 `.csv` 文件。(更多任务支持更新中...)

## 🌆 安装依赖

```bash
pip install -r requirements.txt
```

## 📂 文件结构

- `getGeomagneticData.py` — 包含地磁相关数据(**Dst**, **AE**, **Kp**, **ap**指数)获取函数。
- `getSolarwindData.py` — 包含太阳风相关数据(**ACE**任务)获取函数。

## 🚀 使用说明

### 1. 快速调用示例

```python
# 查询 Dst 指数
dst_df = getGeomagneticData('2023-12', index_type='Dst')

# 查询 AE 指数
ae_df = getGeomagneticData('2023-12', index_type='AE')

# 同时查询 Dst 和 AE 指数
both_df = getGeomagneticData('2023-12', index_type=['Dst', 'AE'])

# Dst指数数据保存为 CSV 文件
dst_df.to_csv(f"Dst_{time}.csv", index=False)

# 查询 ACE 任务获取的太阳风数据
ace_df = getSolarwindData('2023-12', 'ACE', '1h')
```

### 2. 函数接口说明

#### 地磁相关数据获取函数
```python
getGeomagneticData(time, index_type='Dst')
```

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `time` | `str` | 查询时间（格式：`YYYY-MM`） |
| `index_type` | `str` 或 `list` | 要查询的地磁指数，可选 `'Dst'`、`'AE'`、 `'Kpap'`，也可以是它们的列表 |

**返回值：**
- `pandas.DataFrame`，包含以下字段：
  - `Time`（UTC时间）
  - 以及对应的地磁指数数据（如 `Dst`、`AE`、`AL`、`AU`、`AO`、`Kp`、`ap`）

#### 太阳风相关数据获取函数
```python
getSolarwindData(time, mission='ACE', interval='1h')
```

| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `time` | `str` | 查询时间（格式：`YYYY-MM`） |
| `mission` | `str` | 要查询的任务名称，可选 `'ACE'` |
| `interval` | `str` | 要选择的时间分辨率，可选 `1h` 或 `1m` （需要与任务对应） |

**返回值：**
- `pandas.DataFrame`，包含以下字段：
  - `Time`（UTC时间）
  - 以及对应的太阳风相关参数数据（如 `S1`,`ProtonDensity`, `BulkSpeed`, `IonTemperature`, `S2`, `Bx`, `By`, `Bz`, `Bt`, `Lat`, `Lng`）

## ⚠️ 注意事项

- 地磁指数数据源来自 [京都大学WDC地磁中心](https://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html)，[GFZ](https://kp.gfz.de/)。太阳风数据源来自 [NASA](https://sohoftp.nascom.nasa.gov/sdb/)。不同时间段使用不同数据接口，存在数据发布延迟。
- 如遇到请求失败（如返回404错误），请检查：
  - 查询时间段是否已有数据发布。
  - 查询时间是否在支持的数据范围内。
- 对于 AE 数据，目前没有找到2020年数据的下载源。

## 📊 示例输出

部分 Dst 数据示例（2023年12月）：

| Time | Dst |
| :--- | :-- |
| 2023-12-01 00:00:00 | -5 |
| 2023-12-01 01:00:00 | -4 |
| 2023-12-01 02:00:00 | -3 |
| ... | ... |

部分 AE 数据示例（2023年12月）：

| Time | AE | AL | AU | AO |
| :--- | :-: | :-: | :-: | :-: |
| 2023-12-01 00:00:00 | 120 | -80 | 200 | 40 |
| 2023-12-01 00:01:00 | 118 | -79 | 197 | 39 |
| ... | ... | ... | ... | ... |

## 📝 License

本项目仅用于学术交流与学习用途。  
数据版权归 [WDC for Geomagnetism, Kyoto](https://wdc.kugi.kyoto-u.ac.jp/), [GFZ](https://kp.gfz.de/), [ESA](https://soho.nascom.nasa.gov/) 所有。