"""
骰点相关，使用onedice协议
"""
from typing import Optional, Dict, Tuple

from .dice import Lexer, Parser
from .utils import get_alias
    

def random(statement: str = '1d100') -> int:
    """
    使用onedice进行骰点

    Args:
        statement (str, optional): [onedice]公式. 默认为 '1d100'.

    Returns:
        int: 骰点后结果
    """
    return int(Parser(Lexer(statement)).parse())



def RD(player_name: Optional[str], statement: str = '1d100', item: str = '', ) -> str:
    """
    进行骰点并返回骰点消息

    Args:
        player_name: Optional[str] 玩家名字
        item: Optional[str] 检定技能
        statement: str = '1d100' [onedice]骰子检定公式

    Return:
        str 检定后信息
    """
    statement = '1d100' if statement == '1d' or statement == '1' else statement
    print(f"statement:{statement}")
    result = random(statement)
    item = f'[{item}]' if item != '' else ''
    return f"{player_name}的{item}投掷结果：{statement.upper()}={result}"


def RA(player_name: Optional[str], item: str, attr: Optional[int], card: Dict[str, int], PBCls: int) -> str:
    """进行检定并返回骰点信息

    Args:
        player_name (str): 玩家名字
        user_id (int): QQ号
        item (str): 检定技能
        attr (int): 技能值

    Returns:
        str: 检定后信息
    """
    attrs: int = card.get(get_alias(item), 0)
    attrs = attr if attr is not None else attrs
    if (attrs == 0):
        return f'{player_name}没有这个属性'
    result: int = random()
    msg = '失败~'
    exMsg: str = ""
    if PBCls == 1: #Bonus
        PubResult: int = random("1d10")
        exMsg = f"(奖励骰:{result}/{PubResult})"
        result = min(result // 10, PubResult) * 10 + result % 10 
    elif PBCls == 2: #Publish
        PubResult: int = random("1d10")
        exMsg = f"(惩罚骰:{result}/{PubResult})"
        result = max(result // 10, PubResult) * 10 + result % 10
        result = 100 if result > 100 else result
    elif PBCls == 3: #standard rule
        if ((result > 95 and attrs < 50) or result == 10):
            msg = "大失败~"
        if (result <= attrs):
            msg = '成功！'
        if (result <= attrs*0.5):
            msg = '困难成功！'
        if (result <= attrs*0.2):
            msg = "极难成功！"
        if (result == 1):
            msg = "大成功！！"
        return f"{player_name}的[{item}]标准规则检定结果:D100={result}/{attrs} {msg}"
    if (result > 96):
        msg = "大失败~"
    if (result <= attrs):
        msg = '成功！'
    if (result <= attrs*0.5):
        msg = '困难成功！'
    if (result <= attrs*0.2):
        msg = "极难成功！"
    if (result < 4):
        msg = "大成功！！"
    return f"{player_name}的[{item}]检定结果:D100={result}/{attrs} {msg}{exMsg}"

def RA_NUM(player_name: str, attr: int) -> str:
    """进行数字检定并返回骰点信息

    Args:
        player_name (str): 玩家名字
        user_id (int): QQ号
        attr (int): 技能值

    Returns:
        str: 检定后信息
    """
    attrs: int = attr
    result: int = random()
    msg = '失败~'
    if (result > 96):
        msg = "大失败~"
    if (result <= attrs):
        msg = '成功！'
    if (result <= attrs*0.5):
        msg = '困难成功！'
    if (result <= attrs*0.2):
        msg = "极难成功！"
    if (result < 4):
        msg = "大成功！！"
    return f"{player_name}的检定结果:D100={result}/{attrs} {msg}"

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
    STR = random('3d6')*5
    CON = random('3d6')*5
    SIZ = random('2d6+1d8')*5
    DEX = random('3d6')*5
    APP = random("3d6")*5
    INT = random("2d6+6")*5
    EDU = random("2d6+6")*5
    POW = random("2d6+1d8")*5
    LUC = random("3d6")*5
    SUM = STR+CON+SIZ+DEX+APP+INT+EDU+POW
    return f"力量{STR}体质{CON}体型{SIZ}敏捷{DEX}外貌{APP}智力{INT}教育{EDU}意志{POW}幸运{LUC},共计{SUM}/{SUM+LUC}"
