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






# Получим данные для машинного обучения
# eth_usdt = get_info('ETHUSDT')  #print(eth_usdt)
# btc_usdt = get_info('XBTUSDT')  #print(btc_usdt)
# Проведём анализ данных за прошедший час по парам ETHUSDT и XBTUSDT
# prophet_eth_usdt = get_proph(eth_usdt)   #with pd.option_context('display.max_rows', None, 'display.max_columns', None):    #print(prophet_eth_usdt)
# prophet_btc_usdt = get_proph(btc_usdt)   #with pd.option_context('display.max_rows', None, 'display.max_columns', None):    #print(prophet_btc_usdt)
# Проверим корреляцию
# print(prophet_eth_usdt.corrwith(prophet_btc_usdt)['yhat'])

# возьмем ключи из .env
# def configure():
#     load_dotenv()
# configure()

# client = bitmex.bitmex(test=False, api_key=os.getenv('Bit_ID'), api_secret=os.getenv('Bit_Secret'))
# result = client.Quote.Quote_get(symbol="XBTUSDT", reverse=True, count=1).result()
# print(result[0][0]['bidPrice'])
# result[0][0]['bidPrice']
# result[0][0]['bidSize']
# result[0][0]['askPrice']


# Задаем длительность периода в минутах и минимальное процентное изменение цены для вывода сообщения
# period_minutes = 60
# change_threshold = 1
#
# # Основной цикл программы
# while True:
#
#     # Получаем текущую цену фьючерса ETHUSDT
#     current_price = client.futures_symbol_ticker(symbol=future_symbol)['price']
#
#     # Вычисляем процентное изменение цены
#     percent_change = (float(current_price) - float(price)) / float(price) * 100
#
#     # Если процентное изменение превышает порог, выводим сообщение в консоль
#     if abs(percent_change) >= change_threshold:
#         print(f'Цена изменилась на {percent_change:.2f}% за последние {period_minutes} минут')
#
#     # Ждем 1 секунду перед повторной проверкой
#     time.sleep(1)
#
#     # Если прошло достаточно времени, обновляем начальную цену
#     if time.time() - client.futures_klines(symbol=future_symbol, interval=ccxt.Exchange.TIMEFRAMES['1m'])[0][
#         0] / 1000 >= period_minutes * 60:
#         price = current_price




#
# [11 rows x 22 columns]
# trend                         0.999897
# yhat_lower                    0.468887
# yhat_upper                    0.465330
# trend_lower                   0.999897
# trend_upper                   0.999897
# additive_terms                0.999942
# additive_terms_lower          0.999942
# additive_terms_upper          0.999942
# daily                         0.999936
# daily_lower                   0.999936
# daily_upper                   0.999936
# weekly                        0.999366
# weekly_lower                  0.999366
# weekly_upper                  0.999366
# yearly                        0.998612
# yearly_lower                  0.998612
# yearly_upper                  0.998612
# multiplicative_terms               NaN
# multiplicative_terms_lower         NaN
# multiplicative_terms_upper         NaN
# yhat                          0.470321
# dtype: float64
#
# Process finished with exit code 0


# # from statsmodels.tsa.stattools import xcorr
# #
# # # Рассчитываем кросс-корреляцию между двумя временными рядами
# # lags, corr, _, _ = xcorr(eth_usdt['Close'], btc_usdt['Close'], maxlags=None, normed=True, detrend=False)








# prophet_eth_usdt = get_proph(eth_usdt)
# print(prophet_eth_usdt)
# prophet_btc_usdt = get_proph(btc_usdt)
# print(prophet_btc_usdt)

# попробуем линейную регрессию
# LinReg = LinearRegression()
# LinReg.fit(prophet_eth_usdt, prophet_btc_usdt)
# print(LinReg.score(prophet_eth_usdt, prophet_btc_usdt))



# вывести графики ETHUSDT и XBTUSDT
# plt.plot(eth_usdt['close'], label='ETHUSDT')
# plt.plot(btc_usdt['close'], label='XBTUSDT')
# plt.legend()
# plt.show()

# sb.pairplot(eth_usdt)
# eth_usdt.plot()
# plt.show()

# попробуем линейную регрессию
# LinReg = LinearRegression()
# LinReg.fit(eth_usdt, btc_usdt)
# print(LinReg.score(eth_usdt, btc_usdt))


# Чтобы понять, что движение ETHUSDT независимо от XBTUSDT, необходимо проанализировать прогнозируемые значения для
# обоих активов и сравнить их. Если прогнозы для обоих активов имеют схожие тренды и сезонности, то можно предположить,
# что движение ETHUSDT связано с движением XBTUSDT. В таком случае, значительное изменение цены ETHUSDT, вероятно,
# будет вызвано влиянием XBTUSDT.
#
# Если же прогнозы для ETHUSDT и XBTUSDT имеют различные тренды и сезонности, то можно сделать вывод о том, что движение
# ETHUSDT не зависит от движения XBTUSDT, и значительные изменения цены ETHUSDT могут быть вызваны только собственными
# факторами, не связанными с XBTUSDT.
#
# Для сравнения прогнозов можно визуализировать их графически, например, построив





# client = bm.bitmex(
#     test=True,
#     api_key='S8aCaajPT9zs5hCqKubw6_e8',                               #{os.getenv('Bit_ID')},
#     api_secret='Xb-TVv3wJ8xT3fZSu83OFrT0sZPjKx6KUCyvAQFF9JaqT-Ae'     #{os.getenv('Bit_Secret')}
# )
# print(type(client))

# data = client.Trade.Trade_getBucketed(
#     binSize='1h', symbol='ETHUSDT', count='100', reverse=True
# ).result()[0]

# https://www.bitmex.com/api/v1/trade/bucketed?binSize=1h&partial=false&symbol=ETHUSDT&count=100&reverse=false&startTime=2023-03-09
# client = RESTClient(api_key={os.getenv('API_Key')})

# https://api.polygon.io/v2/aggs/ticker/X:BTCUSDT/range/1/hour/2023-01-09/2023-01-09?adjusted=true&sort=asc&limit=120&apiKey=MChJ78zQxDWBYZBxxf9MPuFc6g8z3Ezd
#



