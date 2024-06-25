from datetime import datetime
from re import findall, match
from typing import Dict, Tuple
from typing_extensions import Self
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from .model import DataContainer, LogContents


#将录卡的属性全部统一为第一个值
#而后导出卡片时生成多个属性
same_attr_list: Dict[str, Tuple] = {
    "力量": ("str",),
    "体质": ("con",),
    "体型": ("siz",),
    "敏捷":("dex",),
    "外貌":("app",),
    "智力":("int","灵感"),
    "意志":("pow",),
    "教育":("edu",),
    "幸运":("luc","运气",),
    "理智":("san","理智值",),
    "魔法":("mp",),
    "体力":("hp",),
    "信誉":("信用评级",),
    "计算机使用":("计算机","电脑"),
    "克苏鲁神话":("克苏鲁","cm")
}

def same_list():
        """将同义词并做一个集合"""
        same = set()
        for i in same_attr_list.values():
            same.update(i)
        return same

def get_alias_dict() -> Dict[str, str]:
        """返回属性名字典 {输入属性名:存储属性名}"""
        alias_dict: Dict[str, str] = {}
        for k,v in same_attr_list.items():
            alias_dict[k] = k
            for i in v:
                alias_dict[i] = k
        return alias_dict

SAME = same_list()

ALIAS_DICT = get_alias_dict()

class Attribute:
    """属性类"""

    def __init__(self, args: str):
        self.attrs = self.get_attrs(args)

    def get_attrs(self, msg: str) -> Dict[str, int]:
        """通过正则处理玩家的车卡数据，获取属性值"""
        find: list[tuple[str, int]] = findall(r"(\D{1,10})(\d{1,3})", msg)
        attrs: Dict[str, int] = {}
        for i in find:
            a, b = i
            attrs[get_alias(str(a))] = int(b)
        return attrs
    
    

    def set(self, attr: str, value: int) -> Self:
        """设置属性值"""
        attr = get_alias(attr)
        self.attrs[attr] = value
        return self
    
    def add(self, attr: str, value: int) -> Self:
        """增加属性值"""
        attr = get_alias(attr)
        if self.get(attr)+value > 100:
            self.set(attr, 100)
        else:
            self.set(attr, self.get(attr)+value)
        return self
    
    def minus(self, attr: str, value: int) -> Self:
        """减少属性值"""
        attr = get_alias(attr)
        if self.get(attr)-value < 0:
            self.set(attr, 0)
        else:
            self.set(attr, self.get(attr)-value)
        return self
    
    def extend_attrs(self, attrs: str) -> Self:
        """扩展属性"""
        self.attrs.update(self.get_attrs(attrs))
        return self

    def get(self, attr: str) -> int:
        """获取属性值"""
        attr = get_alias(attr)
        return self.attrs.get(attr, 0)
    
    def dao(self) -> str:
        """导出属性卡"""
        c = self.__str__()
        for k,v in same_attr_list.items():
            if self.get(k) > 0:
                for i in v:
                    c+=f"{i}{self.get(k)}"
        return c
    def set_back(self):
        ...

    def to_str(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        """将玩家的车卡数据转换为字符串"""
        attrs = ""
        for k,v in self.attrs.items():
            attrs += f"{k}{v}"
        return attrs
    
def get_alias(attr: str) -> bool:
        """获取存储属性名"""
        if attr in SAME:
            return ALIAS_DICT[attr]
        return attr

def msg_is_image(event: GroupMessageEvent):
    for seg in event.message:
        if seg.type != "image" and seg.type != "face":
            return False
    return True

def join_log_msg(data: DataContainer, event: MessageEvent):
    """拼接日志消息"""
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        #msg = image_in_msg(event)
        if not msg_is_image(event):
            logs = LogContents(
                event.sender.user_id, #QQ号
                get_name(event), #用户群昵称
                # p_name = event, #角色名  未实装
                event.message.extract_plain_text(), #消息内容
                bool(match(r"^[\(\（]", event.message.extract_plain_text().replace(' ', ''))), #消息是否为以(（开始的内容
                datetime.fromtimestamp(event.time), #消息时间
                # log.u_cls = [数据库用户表查询返回值] #用户区分 0：骰娘本体 1：KP 2：PC 3：闲杂人等  未实装
                event.message_id #消息ID
            )
            data.log_add(group_id, logs)

def join_log_bot_msg(data: DataContainer, event: MessageEvent, msg: str, permitList: list):
    """拼接日志消息"""
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        if group_id in permitList:
            logs = LogContents(
                #event.sender.user_id, 
                event.self_id, #Bot QQ号
                "骰娘", #用户群昵称
                # p_name = event, #角色名  未实装
                #event.message.extract_plain_text(), #消息内容
                msg, #消息内容
                False, #消息是否为以(（开始的内容
                datetime.fromtimestamp(event.time), #消息时间
                # log.u_cls = [数据库用户表查询返回值] #用户区分 0：骰娘本体 1：KP 2：PC 3：闲杂人等  未实装
                event.message_id #消息ID
            )
            data.log_add(group_id, logs)


def get_name(event: MessageEvent) -> str:
    """获取玩家昵称"""
    return event.sender.card if event.sender.card else (event.sender.nickname if event.sender.nickname else "PL")

def get_msg(event: MessageEvent, index: int) -> str:
    """获取消息"""
    return event.message.extract_plain_text()[index:].replace(' ', '').lower()
