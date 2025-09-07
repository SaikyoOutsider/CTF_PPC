from pwn import *
import networkx as nx


def create_map(data):
    map = []
    start, finish = (), ()
    for i in range(1, len(data)):
        map.append([])
        for j in range(len(data[i])):
            if data[i][j] in '#*':
                if data[i][j] == '*':
                    data[i] = data[i].replace('*', '_')
                finish = (i - 1, j)
            elif data[i][j] in '@&':
                if data[i][j] == '&':
                    data[i] = data[i].replace('&', '_')
                start = (i - 1, j)
            if data[i][j] == '|':
                moves = (False, False, False, False)
            elif i == 1:
                moves = (False, j < len(data[i]) - 2 and data[i][j + 1] != '|' and data[i][j + 2] != '|', data[i][j] != '_', j > 1 and data[i][j - 1] != '|' and data[i][j - 2] != '|')
            else:
                moves = (data[i - 1][j] not in '|_', j < len(data[i]) - 2 and data[i][j + 1] != '|' and data[i][j + 2] != '|', data[i][j] != '_', j > 1 and data[i][j - 1] != '|' and data[i][j - 2] != '|')
            map[-1].append(moves)
    return map, start, finish

def solve_lab(map, start, finish):
    solution = []
    G = nx.Graph()
    G.add_nodes_from([(i, j) for i in range(len(map)) for j in range(len(map[i]))])
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j][0]:
                G.add_edge((i, j), (i - 1, j))
            if map[i][j][1]:
                G.add_edge((i, j), (i, j + 2))
            if map[i][j][2]:
                G.add_edge((i, j), (i + 1, j))
            if map[i][j][3]:
                G.add_edge((i, j), (i, j - 2))
    path = nx.shortest_path(G, start, finish)
    print(path)
    for i in range(1, len(path)):
        if path[i][0] - path[i - 1][0] == -1:
            solution.append('N')
        elif path[i][0] - path[i - 1][0] == 1:
            solution.append('S')
        elif path[i][1] - path[i - 1][1] == 2:
            solution.append('E')
        else:
            solution.append('W')

    return solution


conn = remote("tasks.duckerz.ru", 30003)

for _ in range(3):
    conn.sendline('1')
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

    print(data)

    data = data[9:-7]
    data[0] = data[0][3:]
    for i in range(len(data)):
	    data[i] = data[i].replace('\n', '')
	    data[i] = data[i].replace('\x1b[31;4m#\x1b[0m', '*')
	    data[i] = data[i].replace('\x1b[31m#\x1b[0m', '#')
	    data[i] = data[i].replace('\x1b[32;4m@\x1b[0m', '&')
	    data[i] = data[i].replace('\x1b[32m@\x1b[0m', '@').strip()

    for item in data:
        print(item)
    map, start, finish = create_map(data)
    solution = solve_lab(map, start, finish)

    print(solution)
    
    # Отправляем ответ на сервер
    for item in solution:
        conn.sendline('3')
        conn.sendline(item)
        data = conn.recv(timeout=0.1).decode('utf-8')
        print(data)
        if 'Error' in data:
        	conn.sendline('1')
        	data = conn.recv(timeout=0.5).decode('utf-8')
        	print(data)
        	time.sleep(0.5)
        	print(item)
        	conn.interactive()
        	time.sleep(60)
        #time.sleep(0.5)

# Получаем флаг
resp = conn.recvall()
print(resp.decode('utf-8'))
# После завершения всех задач закрываем соединение
conn.close()
