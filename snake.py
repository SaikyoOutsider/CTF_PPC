from pwn import *
import time

def solve(data):
    # Удаляем необрабатываемые строки
    while set(data[0]) != {'+', '-', '\n'}:
      del data[0]
    # Удаляем горизонтальную рамку
    data = list(filter(lambda x: set(x) != {'+', '-', '\n'} and x != '\n', data))
    data_parsed = []
    last = -1
    for i in range(len(data)):
        # Сплитим строки по | (важно, что не по пробелам)
        # Чтобы получившиеся массивы были одинаковой длины
        buff = [sym for sym in data[i].split('|') if sym != '\n' and sym != '']
        # В новой переменной уже оставляем только значения, исключая ненужные пробелы
        buff_parsed = [sym for sym in buff if sym.strip() != '']
        # Если индекс первого элемента в нашей необработанной строки отличается
        # от индекса последнего элемента предыдущей строки (змейка развернулась налево)
        if i != 0 and buff.index(buff_parsed[0]) != last:
            # Реверсим нашу строку
            buff_parsed.reverse()
        # Сохраняем индекс последнего элемента для последующих проверок
        last = buff.index(buff_parsed[-1])
        # Сохраняем получившуюся строку
        data_parsed.append(''.join([sym.strip() for sym in buff_parsed]))
    # Объединяем полученное выражение, вычисляем и возвращаем
    res_expression = ''.join(data_parsed)
    return eval(res_expression)

conn = remote("qookie.tech", 30002)

for _ in range(100):  # Если нужно выполнить 100 задач
    data = []
    while True:
        try:
            line = conn.recvline(timeout=0.1).decode('utf-8')
            if line:  # Если получили строку, добавляем её в буфер
                print(line.strip())  # Для отладки, можно убрать
                data.append(line)
        except EOFError:
            print("Соединение закрыто сервером")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break
        
        # Проверяем паузу в поступлении данных
        # Если данные не поступали в течение 0.1 секунды, считаем задачу полной
        if not line:
            time.sleep(0.1)
            # Проверяем снова, если снова пусто, значит задача завершена
            try:
                next_line = conn.recvline(timeout=0.1).decode('utf-8')
                if not next_line:
                    break
                else:
                    data.append(next_line.strip())
            except:
                break

    answer = solve(data)
    print(answer)

    # Отправляем ответ на сервер
    conn.sendline(str(answer))

# Получаем флаг
resp = conn.recvall()
print(resp.decode('utf-8'))
# После завершения всех задач закрываем соединение
conn.close()
