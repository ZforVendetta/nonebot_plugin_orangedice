import re
import math

from .prandom import random

def roll_dice(dice_notation):
    match = re.fullmatch(r'(\d+)?[Dd](\d+)?', dice_notation)
    if not match:
        raise ValueError(f"Invalid dice notation: {dice_notation}")
    
    count = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2)) if match.group(2) else 100
    rolls = [random(1, sides) for _ in range(count)]
    result = sum(rolls)
    exMsg = f'{count}D{sides}'
    return result, exMsg

def process_expression(expression):
    parts = re.split(r'(\s*[\+\-\*xX/]\s*)', expression)
    
    # 初始化总和
    total, exMsg = roll_dice(parts[0].strip())
    
    # 遍历表达式的其余部分并计算总和
    i = 1
    while i < len(parts):
        if i == 1:
            exMsg += f'({total})'
        operator = parts[i].strip()
        next_part = parts[i + 1].strip()
        if next_part.isdigit():
            next_value = int(next_part)
            next_exMsg = next_part
        else:
            next_value, next_exMsg = roll_dice(next_part)
            next_exMsg += f'({next_value})'
        
        if operator == '+':
            exMsg += '+'
            total += next_value
        elif operator == '-':
            exMsg += '-'
            total -= next_value
        elif operator in ['*', 'x', 'X']:
            exMsg += '*'
            total *= next_value
        elif operator == '/':
            exMsg += '/'
            total = math.ceil(total / next_value)
        else:
            print(next_exMsg)
        exMsg += next_exMsg
        i += 2
    
    return total, exMsg

def process_command(command: str):
    command = command.replace(" ","")
    # print(command)
    exMsg = ''
    diceCls = ''
    if re.match(r'[abpc]\S+', command):
        match = re.fullmatch(r'([abpc])\S+', command)
        if match:
            prefix = match.group(1)
            rand_value = random(1, 100)
            result = rand_value
            if prefix == 'a':
                diceCls = 'a'
            elif prefix == 'b':
                diceCls = 'b'
                rand_value2 = random(1, 10)
                result = (min(rand_value // 10, rand_value2) * 10) + (rand_value % 10)
                exMsg = f'(奖励骰:{rand_value}|{rand_value2})'
            elif prefix == 'p':
                diceCls = 'p'
                rand_value2 = random(1, 10)
                if rand_value2 == 10:
                    result = 100
                else:
                    result = (max(rand_value // 10, rand_value2) * 10) + (rand_value % 10)
                exMsg = f'(惩罚骰:{rand_value}|{rand_value2})'
            elif prefix == 'c':
                diceCls = 'c'
                exMsg = f'(标准规则书)'
            return result, diceCls, exMsg
        else:
            return result, diceCls, exMsg
    elif re.match(r'(\d+)?[Dd](\d+)?([\+\-\*xX/]\d*[Dd]\d+)*', command):
        result, exMsg = process_expression(command)
        diceCls = 'd'
        return result, diceCls, exMsg
    
    else:
        exMsg = '(Error!)'
        return 0,99,exMsg



# for test

# commands = [
#     "d",
#     "2d6+1d8",
#     "2D6+1D8",
#     "2D6+1D8*5",
#     "2D6+1D8 *5",
#     "3D6 *5",
#     "d55",
#     "d1000",
#     "d-100",
#     "100d2",
#     "2d50 / 3d5",
#     "a 测试",
#     "a 测试",
#     "a 测试",
#     "c 速度",
#     "c 速度",
#     "c 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "p 速度",
#     "b 速度",
#     "d10 + 5d3",
#     "2d5 * 2d4",
#     "2d5 * 2d4 + 1d3",
#     "a60",
#     "1d5 x 1d2",
#     "2d5 - 2d2"
# ]

# for cmd in commands:
#     try:
#         result, diceCls, exMsg = process_command(cmd)
#         print(f"Command: {cmd}, Result: {result}, diceCls: {diceCls}, exMsg: {exMsg}")
#     except ValueError as e:
#         print(f"Command: {cmd}, Error: {e}")
