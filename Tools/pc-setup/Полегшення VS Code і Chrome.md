# Полегшення VS Code і Chrome на шкільних ПК

Скрипти для старих шкільних комп'ютерів: Python ведемо в Thonny, а HTML/CSS/JS — у VS Code, тому VS Code полегшуємо.

Що роблять обидва скрипти:

1. Записують легкі налаштування VS Code: без AI-функцій, телеметрії, оновлень, мінікарти й Git. Старі налаштування зберігаються як `settings.json.bak`.
2. Видаляють важкі розширення: Python, Pylance, Copilot.
3. Вмикають у Chrome Memory Saver і забороняють йому працювати у фоні після закриття.

## Як запускати

- **Linux:** під обліковим записом учня `bash optimize-school-linux.sh` (для частини з Chrome попросить пароль sudo).
- **Windows:** під обліковим записом учня правою кнопкою на `optimize-school-windows.bat` → «Запуск від імені адміністратора».

Запускати **один раз** на комп'ютер: повторний запуск перезапише `settings.json.bak` налаштуваннями самого скрипта.

Перевірити, що політики Chrome застосувалися: `chrome://policy`.

## Як скасувати

- VS Code: перейменувати `settings.json.bak` назад у `settings.json`.
- Chrome на Windows (від адміністратора): `reg delete "HKLM\SOFTWARE\Policies\Google\Chrome" /f`
- Chrome на Linux: `sudo rm /etc/opt/chrome/policies/managed/school.json`

## Windows 7 і 32-бітні ПК

Скрипти нічого не зламають, але VS Code там застарілий (останні версії: 1.70.3 для Windows 7, 1.83 для 32-біт). На таких машинах для JS краще Notepad++ поруч із браузером.
