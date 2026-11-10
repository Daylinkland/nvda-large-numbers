LARGE NUMBER READER 1.2 - for NVDA
==================================

English
-------
A small NVDA add-on that reads long numbers as words instead of one digit at
a time, in English or Spanish. It works with any voice: Microsoft SAPI,
eSpeak, Vocalizer, whatever you use, because it changes the words NVDA
speaks, not the voice.

  Before (English):  "one two three five eight nine two"
  After  (English):  "one million two hundred thirty five thousand eight
                      hundred ninety two"
  After  (Spanish):  "un millón doscientos treinta y cinco mil ochocientos
                      noventa y dos"

Also:
  1500000          -> one million five hundred thousand / un millón quinientos mil
  1000000000000000 -> one quadrillion / mil billones
  up to 36 digits

The number language follows NVDA's own language automatically. A Spanish
NVDA speaks Spanish numbers with no setting at all. To force a language, open
NVDA menu, Preferences, Settings, Large Number Reader, and choose it.

Toggle: NVDA+8 turns it on and off, and NVDA remembers your choice.
Change the key in NVDA menu, Preferences, Input Gestures, Large Number Reader.


How to install
--------------
You need NVDA 2025.1 or newer.

1. Unzip this download to any folder.
2. In that folder, press Enter on largeNumberReader-1.2.nvda-addon
   (or right click it and choose Install).
3. NVDA asks whether to install the add-on. Answer Yes.
4. NVDA offers to restart. Let it restart, and it is active.

If you already installed an earlier version, NVDA will ask whether to update
it. Answer Yes, then let NVDA restart.

To check it is there: NVDA menu, Tools, Add-on Store, Installed add-ons,
look for "Large Number Reader".


Trying it
---------
Open Notepad, type 1235892, and arrow back over it. Then press NVDA+8 and
arrow over it again to hear the difference. Press NVDA+8 once more to turn it
back on.


What it leaves alone
--------------------
- numbers shorter than seven digits, so 500000 and normal numbers are read
  exactly as before
- IDs with a leading zero, like 01234567
- numbers glued to letters, like 0x1234567
- versions and IP addresses, like 2026.2 or 192.168.1.100
- phone number pairs, like 555-1234567
- numbers right after a currency sign, like $1234567
- spelling and character by character reading

Comma grouped numbers work too: 1,235,892 is read the same as 1235892.


Limits
------
- Braille and the text on screen still show the digits; only speech changes.
- Past 36 digits it still breaks the number into three digit groups instead of
  one long string, but without scale names.
- Spanish uses the long scale: billón is a million millions (10^12), and a
  thousand millions is "mil millones".
- It is free to use and share.


How to remove it
----------------
NVDA menu, Tools, Add-on Store, Installed add-ons, select Large Number
Reader, Remove. It writes no files of its own, so nothing is left behind.


Español
-------
Un complemento pequeño para NVDA que lee los números largos con palabras en
vez de dígito por dígito, en inglés o en español. Funciona con cualquier voz,
porque cambia las palabras que NVDA dice, no la voz.

  Antes:  "uno dos tres cinco ocho nueve dos"
  Ahora:  "un millón doscientos treinta y cinco mil ochocientos noventa y dos"

También:
  1500000          -> un millón quinientos mil
  1000000000000000 -> mil billones
  hasta 36 dígitos

El idioma de los números sigue el idioma de NVDA automáticamente. Si tu NVDA
está en español, ya dirá los números en español sin tocar nada. Para elegir el
idioma a mano: menú NVDA, Preferencias, Opciones, Large Number Reader.

Tecla: NVDA+8 lo activa y lo desactiva, y NVDA recuerda la elección.

Instalar:
1. Descomprime la descarga en una carpeta.
2. Pulsa Enter sobre largeNumberReader-1.2.nvda-addon.
3. NVDA pregunta si quieres instalarlo. Di que sí.
4. NVDA ofrece reiniciar. Deja que reinicie y ya funciona.

Si ya tenías una versión anterior, NVDA preguntará si quieres actualizarla.
Di que sí y deja que reinicie.

Para comprobarlo: menú NVDA, Herramientas, Tienda de complementos,
Complementos instalados, busca "Large Number Reader".

No cambia los números de menos de siete dígitos, ni las fechas, versiones,
direcciones IP, identificadores con cero delante, ni los números de teléfono.

En español se usa la escala larga: billón es un millón de millones (10^12), y
mil millones se dice "mil millones".

Para quitarlo: menú NVDA, Herramientas, Tienda de complementos,
Complementos instalados, Large Number Reader, Quitar.
