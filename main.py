


from fastapi import FastAPI, Query, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd

from datetime import date,datetime,timedelta
import calendar

###
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import hashlib


# 验证令牌的函数

# 初始化安全方案
bearer_scheme = HTTPBearer()

stored_token = {
    "/get_year_fortune": "your_year_token",
    "/get_month_fortune": "your_month_token",
    "/get_week_fortune": "your_week_token",
    "/get_day_fortune": "your_day_token",
    "/get_couples_horoscope": "your_couples_token"
}

# 验证令牌的函数
def verify_token(request: Request,
                 credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    验证请求中的令牌，只针对一级路径
    """
    global stored_token
    # 提取一级路径
    endpoint = '/' + request.url.path.strip('/').split('/', 1)[0]
    logging.info(f"Verifying token for endpoint: {endpoint}")

    if endpoint not in stored_token:
        raise HTTPException(status_code=500,
                            detail="Token for endpoint not loaded")

    token = credentials.credentials
    if token != stored_token[endpoint]:
        raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI()

# 加载数据到内存
df_year_fortune = pd.read_csv("year_fortune.csv",encoding='utf-8')
df_month_fortune = pd.read_csv("month_fortune.csv",encoding='utf-8')
df_week_fortune = pd.read_csv("week_fortune.csv",encoding='utf-8')
df_day_fortune = pd.read_csv("every_today_horoscope.csv",encoding='utf-8')
df_couples_horoscope = pd.read_csv("Couples_Horoscope.csv",encoding='utf-8')


#### 根据constellation来读取年信息
####星座单词列表
# constellation_list = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

###测试

##每年的运势
@app.get("/get_year_fortune/{constellation}",dependencies=[Depends(verify_token)])
def get_year_fortune(constellation: str,
                     year: int = Query(None, ge=1900, le=2100)):

    # 如果没有提供年份，默认使用当前年份
    if year is None:
        year = datetime.now().year

    # 检查是否存在该星座
    if constellation not in df_year_fortune['yearFortune'].values:
        return JSONResponse(content={"error": "未找到该星座"}, status_code=404)

    # 获取该星座的行数据
    row = df_year_fortune[(df_year_fortune['yearFortune'] == constellation) & (df_year_fortune['year'] == year) ].iloc[0]

    # 构建返回数据
    result = {
        "constellation": constellation,
        "horoscopeDescription": row.get("horoscopeDescription", ""),
        "overallFortune": row.get("overallFortune", ""),
        "loveFortune": row.get("loveFortune", ""),
        "workFortune": row.get("workFortune", ""),
        "financialFortune": row.get("financialFortune", ""),
        "healthFortune": row.get("healthFortune", ""),
        "summary": row.get("summary", "")
    }

    return result



# #####星座单词列表
# constellation_list = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
# month的格式为2025-03
###每年的运势
@app.get("/get_month_fortune/{constellation}/{month}",dependencies=[Depends(verify_token)])
def get_month_fortune(constellation: str,month: str):
    # 检查是否存在该星座
    if constellation not in df_month_fortune['monthFortune'].values or month not in df_month_fortune['month'].values:
        return JSONResponse(content={"error": "未找到该星座或月份"}, status_code=404)

    # 获取该星座和月份对应的一行数据
    row = df_month_fortune[(df_month_fortune['monthFortune'] == constellation) & (df_month_fortune['month'] == month)].iloc[0]

    ####根据month来获得本月的所有的天数日期

    # 解析年份和月份
    year, month = map(int, month.split("-"))

    # 获取该月天数
    days = calendar.monthrange(year, month)[1]

    # 构造所有日期列表
    date_list = [date(year, month, day).isoformat() for day in range(1, days + 1)]

    l = {}
    for date_l in date_list:
        row = df_day_fortune[(df_day_fortune['todayFortune'] == constellation) & (df_day_fortune['time'] == date_l)].iloc[0]

        l[date_l] = row.get("score", "")

    # 构建返回数据
    result = {
        "constellation": constellation,
        "horoscopeDescription": row.get("horoscopeDescription", ""),
        "overallFortune": row.get("overallFortune", ""),
        "loveFortune": row.get("loveFortune", ""),
        "workFortune": row.get("workFortune", ""),
        "financialFortune": row.get("financialFortune", ""),
        "healthFortune": row.get("healthFortune", ""),
        "summary": row.get("summary", ""),
        "month_scores": l
    }
    return result


# print(df_week_fortune[(df_week_fortune['weekFortune'] == "Aries") & (df_week_fortune['week'] == 10)].iloc[0])

@app.get("/get_week_fortune/{constellation}/{week}",dependencies=[Depends(verify_token)])
def get_week_fortune(constellation: str,week: int):
    # 检查是否存在该星座
    if constellation not in df_week_fortune['weekFortune'].values or week not in df_week_fortune['week'].values:
        return JSONResponse(content={"error": "未找到该星座或对应的周"}, status_code=404)

    # 获取该星座和月份对应的一行数据
    row = df_week_fortune[(df_week_fortune['weekFortune'] == constellation) & (df_week_fortune['week'] == week)].iloc[0]

    ####获得当前年份对应的自然周
    year = datetime.now().year  # 当前年份
    first_day = datetime.fromisocalendar(year, week, 1)  # 周一
    date_list = [(first_day + timedelta(days=i)).date().isoformat() for i in range(7)]

    l = {}
    for date_l in date_list:
        row = df_day_fortune[(df_day_fortune['todayFortune'] == constellation) & (df_day_fortune['time'] == date_l)].iloc[0]
        l[date_l] = row.get("score", "")

    # 构建返回数据
    result = {
        "constellation": constellation,
        "horoscopeDescription": row.get("horoscopeDescription", ""),
        "overallFortune": row.get("overallFortune", ""),
        "loveFortune": row.get("loveFortune", ""),
        "workFortune": row.get("workFortune", ""),
        "financialFortune": row.get("financialFortune", ""),
        "healthFortune": row.get("healthFortune", ""),
        "summary": row.get("summary", ""),
        "month_scores": l
    }
    return result


# print(df_day_fortune['time'].values)
#####当前时间的格式     2025-01-09

@app.get("/get_day_fortune/{constellation}/{date}",dependencies=[Depends(verify_token)])
def get_day_fortune(constellation: str,date: str):

    # 检查是否存在该星座
    if constellation not in df_day_fortune['todayFortune'].values or date not in df_day_fortune['time'].values:
        return JSONResponse(content={"error": "未找到该星座或日期"}, status_code=404)

    # 获取该星座和每天对应的一行数据
    row = df_day_fortune[(df_day_fortune['todayFortune'] == constellation) & (df_day_fortune['time'] == date)].iloc[0]

    # 构建返回数据
    result = {
        "constellation": constellation,
        "horoscopeDescription": row.get("horoscopeDescription", ""),
        "overallFortune": row.get("overallFortune", ""),
        "dayFortune": row.get("dayFortune", ""),
        "workFortune": row.get("workFortune", ""),
        "financialFortune": row.get("financialFortune", ""),
        "healthFortune": row.get("healthFortune", ""),
        "summary": row.get("summary", ""),
        "score": row.get("score", "")
    }
    return result



# row = df_couples_horoscope[(df_couples_horoscope['maleConstellation'] == "Cancer") & (df_couples_horoscope['femaleConstellation'] == "Scorpio")].iloc[0]
#
# print(row)
##情侣占星
@app.get("/get_couples_horoscope/{male_constellation}/{female_constellation}",dependencies=[Depends(verify_token)])
def get_couples_horoscope(male_constellation: str,female_constellation: str):
    # 检查是否存在该星座
    if male_constellation not in df_couples_horoscope['maleConstellation'].values or female_constellation not in df_couples_horoscope['femaleConstellation'].values:
        return JSONResponse(content={"error": "输入的星座错误"}, status_code=404)

    matched_rows = df_couples_horoscope[
        (df_couples_horoscope['maleConstellation'] == male_constellation) &
        (df_couples_horoscope['femaleConstellation'] == female_constellation)
        ]

    # 获取该星座和每天对应的一行数据
    if matched_rows.empty:
        return JSONResponse(content={"error": "未找到匹配的星座组合"}, status_code=404)

    row = matched_rows.iloc[0]
    # 构建返回数据
    result = {
        "male_constellation": male_constellation,
        "female_constellation": female_constellation,
        "pairingAnalysis": row.get("pairingAnalysis", ""),
        "advantages": row.get("advantages", ""),
        "challenges": row.get("challenges", ""),
        "summary": row.get("summary", ""),
        "maleScore": int(row.get("maleScore", 0)) if pd.notna(row.get("maleScore")) else None,
        "femaleScore": int(row.get("femaleScore", 0)) if pd.notna(row.get("femaleScore")) else None,
        "matchScore": int(row.get("matchScore", 0)) if pd.notna(row.get("matchScore")) else None
    }
    return result




# if __name__ == '__main__':
#     print(get_couples_horoscope("Cancer","Scorpio"))



















