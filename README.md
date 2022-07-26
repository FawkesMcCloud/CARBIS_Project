# Тестовое задание

# Системные требования
- ОС: Windows 7+
- Активное интернет соеденение

# Руководство
Запуск программы осуществляется путем открытия файла Search.exe

При запуске прграммы появляется окно косноли с главным меню и инструкцией. 
> Обратите внимание, что при первом запуске программы необходимо установить токен API.

В случае ввода любой строки кроме зарезервированых слов "exit" и "options", будет выполнен поиск на соответсвия.
> В случае ошибки, в консоле будет показано информационное сообщение.

Когда совпадения найдены, будет предложено выбрать одно из совпадений для дальнейшего отображения координат или вернутся назад.
Для выбора варианта введите число. Например "1", для выбора первого варианта или "0" для возвращения назад. 

Для продолжения работы и ввода следующей команды необходимо нажать Enter.

## Настройки

В случае ввода ключевого слова "options", программа войдет в меню настроек.
> Сохранение настроек происходит в файл config.db который будет создан при первом запуске программы

В данном подменю на выбор будут представленны следующие варинты:
- Изменение токена;
- Изменение URL;
- Смена языка (отображение в результатах поиска)
- Назад

