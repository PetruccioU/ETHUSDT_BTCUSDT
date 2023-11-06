# Для определения собственных движений цены пары ETHUSDT, исключив из них движения вызванные
# влиянием цены BTCUSDT, я бы использовал анализ с помощью библиотеки fbprophet, интерфейс которой
# схож с интерфейсом линейной регрессии.
#
# Создадим временные ряды из 60 сэмплов по 1 минуте содержащие данные об изменении курсов валютных пар
# ETHUSDT и BTCUSDT, сохранив из них временную метку и основное значение цены как датафрэйм pandas.
#
# Проверим корреляцию этих двух рядов, с помощью функции df1.corrwith(df2), нас будет интересовать
# насколько сильна корреляция велицины 'yhat' как корреляции величины цен.
#
# Создадим функции для проведения описанного анализа, с возможностью выбора валютных пар и
# интересующего порогового значения корреляции 'yhat', как параметров функции.


# FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME FIXME
import time, requests
from datetime import datetime
import pandas as pd
from prophet import Prophet

# создадим функцию для получения данных для обучения модели prophet:
def get_info(symbol: str):
    now = datetime.now()
    utc_now = now.utcnow()
    unixtime = time.mktime(utc_now.utctimetuple())
    since = datetime.fromtimestamp(unixtime - 70 * 60)

    # получим данные о движении валютной пары для последующего анализа корреляции
    url = 'https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=' + symbol + '&count=60&reverse=false&startTime='+str(since)
    res = requests.get(url)
    data = res.json()

    # получим данные о движении валютной пары для определения её изменения на 1% за час
    url_h = 'https://www.bitmex.com/api/v1/trade/bucketed?binSize=5m&partial=false&symbol=' + symbol + '&count=14&reverse=false&startTime=' + str(since)
    res_h = requests.get(url_h)
    data_h = res_h.json()

    # Сохраним данные в датафрэйм pandas для последующего анализа корреляции
    ohlc = pd.DataFrame(
        data[::-1], columns=['timestamp', 'close']
    )    # .set_index('timestamp')
    ohlc = ohlc.shift(-1)[:-1]
    ohlc.columns = ['ds', 'y']
    ohlc['ds'] = pd.to_datetime(ohlc['ds'])       # преобразуем в дататайм
    ohlc['ds'] = ohlc['ds'].dt.tz_localize(None)    # отбросим таймзону

    # Сохраним данные в датафрэйм pandas для определения её изменения на 1% за час
    ohlc_h = pd.DataFrame(
        data_h[::-1], columns=['timestamp', 'close']
    )    # .set_index('timestamp')
    ohlc_h = ohlc_h.shift(-1)[:-1]
    ohlc_h.columns = ['ds', 'y']
    ohlc_h['ds'] = pd.to_datetime(ohlc_h['ds'])       # преобразуем в дататайм
    ohlc_h['ds'] = ohlc_h['ds'].dt.tz_localize(None)    # отбросим таймзону
    return ohlc, ohlc_h

# Попробуем проанализировать данные о передвижении валютных пар используя prophet, обернув в функцию get_proph(symbol)
def get_prophet(symbol: str):
    model = Prophet(weekly_seasonality=True, daily_seasonality=True, yearly_seasonality=True)
    model.fit(symbol)
    future = model.make_future_dataframe(periods=0)
    forecast = model.predict(future)
    model.plot_components(forecast)
    return forecast

# Проверим корреляцию величин yhat у времянных рядов ETHUSDT и BTCUSDT
def get_corr_from_two_symbols(symbol1, symbol2):
    val1 = get_info(symbol1)[0]
    val2 = get_info(symbol2)[0]
    prophet_val1 = get_prophet(val1)
    prophet_val2 = get_prophet(val2)
    return prophet_val1.corrwith(prophet_val2)['yhat']

# Создадим функцию для анализа изменения пары symbol1 независимого от пары symbol2
def main_cycle(symbol1: str, symbol2: str, precision: float):
    while True:
        is_independent = False
        analyse = get_corr_from_two_symbols(symbol1, symbol2)
        if precision > analyse:
            is_independent = True
        price_now = get_info(symbol1)[1]['y'][0]
        price_dif = get_info(symbol1)[1]['y'][12] - get_info(symbol1)[1]['y'][0]
        if abs(price_dif)/price_now > 0.01 and is_independent:
            print(f'Цена изменилась на {round((abs(price_dif)/price_now)*100, 2):.2f}% процента за последние 60 минут')
            # print((abs(price_dif)/price_now)*100)
            # print(analyse)
            # print(is_independent)
        #else:
            # print(f'Цена изменилась всего на {round((abs(price_dif) / price_now) * 100, 2):.2f}% процента за последние 60 минут')
            # print(analyse)
            # print(is_independent)
        time.sleep(60*60)

# Вызовем функцию для отслеживания движения пары ETHUSDT на 1% в течении последнего времени, независимо от XBTUSDT
main_cycle('ETHUSDT', 'XBTUSDT', 0.4)








