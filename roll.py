"""
骰点相关，使用onedice协议
"""
from typing import Optional, Dict, Tuple

from .dice import process_command
from .utils import get_alias
    

def random(statement: str = '1d100') -> int:
    """
    使用onedice进行骰点

    Args:
        statement (str, optional): [onedice]公式. 默认为 '1d100'.

    Returns:
        int: 骰点后结果
    """
    dice, _, _ = process_command(statement)
    return dice

def checkDice(dice: int, diceCls: str, attrs: int):
    msg = "失败~"
    if diceCls == "c": #标准规则书
        if ((dice > 95 and attrs < 50) or dice == 100):
            msg = "大失败~"
        elif (dice == 1):
            msg = "大成功！！"
        elif (dice <= attrs*0.2):
            msg = "极难成功！"
        elif (dice <= attrs*0.5):
            msg = '困难成功！'
        elif (dice <= attrs):
            msg = '成功！'
    elif diceCls in ["a","p","b"]:
        if (dice > 96):
            msg = "大失败~"
        elif (dice < 4):
            msg = "大成功！！"
        elif (dice <= attrs*0.2):
            msg = "极难成功！"
        elif (dice <= attrs*0.5):
            msg = '困难成功！'
        elif (dice <= attrs):
            msg = '成功！'
    return msg

def TEST_R(player_name: Optional[str], item: Optional[str], card: Optional[Dict[str, int]], cmd: str):
    dice, diceCls, exMsg = process_command(cmd)
    if diceCls != 'd':
        attrs: int = card.get(get_alias(item), 0)
        if (attrs == 0):
            return f'{player_name}没有这个属性'
        else:
            msg = checkDice(dice, diceCls, attrs)
            return f"{player_name}的检定结果:D100={dice}/{attrs} {msg}{exMsg}"
    else:
        return f"{player_name}的检定结果:{exMsg}={dice}。"
        

def SC(player_name: str , san: int, fdice: str, sdice: str) -> Tuple[str, int]:
    """理智检定返回骰点信息

    Args:
        player_name (str): 玩家名字
        san (int): 理智值
        fdice (str): 失败检定表达式
        sdice (str): 成功检定表达式
        
    Returns:
        str, int: 检定结果, 损失理智值
    """
    result: int = random() 
    msg = '失败~' if result > san else '成功！'
    drop_san = random(fdice) if result > san else random(sdice)
    return f"{player_name}的理智检定结果:D100={result} {msg}\n损失{drop_san}理智值 剩余理智值{san-drop_san}", drop_san

def COC() -> str:
    """
    生成COC角色卡
    
    Returns:
        str: 角色卡信息
    """
    STR = random('3d6*5')
    CON = random('3d6*5')
    SIZ = random('2d6+1d8*5')
    DEX = random('3d6*5')
    APP = random("3d6*5")
    INT = random("2d6+6*5")
    EDU = random("2d6+6*5")
    POW = random("2d6+1d8*5")
    LUC = random("3d6*5")
    SUM = STR+CON+SIZ+DEX+APP+INT+EDU+POW
    PER1 = '{:.0f}%'.format(SUM/650*100)
    PER2 = '{:.0f}%'.format((SUM+LUC)/730*100)
    return f"力量{STR}体质{CON}体型{SIZ}敏捷{DEX}外貌{APP}智力{INT}教育{EDU}意志{POW}幸运{LUC},共计{SUM}/{SUM+LUC}({PER1}/{PER2})"
