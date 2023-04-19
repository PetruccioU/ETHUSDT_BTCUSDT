Задание: Напишите программу на Python, которая в реальном времени 
(с минимальной задержкой) следит за ценой фьючерса ETHUSDT и используя выбранный 
вами метод, определяет собственные движение цены ETH, независимое от BTCUSDT. При 
изменении цены на 1% за последние 60 минут, программа выводит сообщение в консоль. 
При этом программа должна продолжать работать дальше, постоянно считывая актуальную цену. 

Решение(FIXME)
Для определения собственных движений цены пары ETHUSDT, исключив из них движения вызванные
влиянием цены BTCUSDT, я бы использовал анализ с помощью библиотеки fbprophet, интерфейс которой
схож с интерфейсом линейной регрессии.

Создадим временные ряды из 60 сэмплов по 1 минуте содержащие данные об изменении курсов валютных пар
ETHUSDT и BTCUSDT, сохранив из них временную метку и основное значение цены как датафрэйм pandas.

Проверим корреляцию этих двух рядов, с помощью функции df1.corrwith(df2), нас будет интересовать
насколько сильна корреляция велицины 'yhat' как корреляции величины цен.

Создадим функции для проведения описанного анализа, с возможностью выбора валютных пар и
интересующего порогового значения корреляции 'yhat', как параметров функции.