"""
sqlmodel很直观,但我不会用。sqlmodel => SQLAlchemy
"""

import pandas as pd
import os
import sqlalchemy
from nonebot import get_plugin_config
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, select, MetaData, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, clear_mappers, registry
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from dataclasses import dataclass
from datetime import datetime

from .config import Config

Base = declarative_base()
metadata = MetaData()
mapper_registry = registry()

del_confirm_dict = []


@dataclass
class LogContents:
    u_id: int
    u_name: str
    msg: str
    comment_flg: bool
    time: datetime
    msg_id: int


class Player(Base):
    __tablename__ = 'PLAYER'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True)
    skills = Column(String)


class GroupLOG(Base):
    __tablename__ = 'GROUP_LOG_MAP'
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, unique=True)  # 群号
    parent_group_id = Column(Integer, default=0)  # 大群群号（秘密团小群用）
    log_on = Column(Boolean, default=False)  # log记录开关
    name = Column(String, default="")  # log名
    end_flag = Column(Boolean, default=False)  # 是否已结束
    del_flag = Column(Boolean, default=False)  # 是否已删除 据此定期清理，或在新建时清空之前的记录


def create_groupId_table(groupId: int):
    table_name = f"GROUP_{groupId}_LOG"
    
    if table_name in metadata.tables:
        return metadata.tables[table_name]

    group_table = Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True), # 记录自增id
        Column('u_id', Integer), # 用户qq号
        Column('u_name', String), # 用户群昵称
        Column('p_name', String), # 角色名
        Column('msg', String), # 消息内容
        Column('comment_flg', Boolean, default=False), # 消息是否为以(（开始的内容
        Column('time', DateTime), # 消息时间
        Column('u_cls', Integer), # 用户区分 0：骰娘本体 1：KP 2：PC 3：闲杂人等
        Column('del_flag', Boolean, default=False), # 是否撤回
        Column('msg_id', Integer), # 内部用消息ID -> 用于更新撤回
    )

    return group_table

class Log(object):
    def __init__(self, u_id, u_name, msg, comment_flg, time, del_flag, msg_id):
        self.id = None
        self.u_id = u_id
        self.u_name = u_name
        # self.p_name = p_name
        self.msg = msg
        self.comment_flg = comment_flg
        self.time = time
        # self.u_cls = u_cls
        self.del_flag = del_flag
        self.msg_id = msg_id

def get_group_log_class(engine, table_name: int):
    log_table = Table(table_name, metadata, autoload=True, autoload_with=engine)
    mapper(Log, log_table)
    return log_table

class DataContainer:

    def __init__(self):
        config = get_plugin_config(Config)
        self.sqlite_file = config.sqlite_file
        self.engine = create_engine(f"sqlite:///{self.sqlite_file}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_card(self, user_id: int) -> Player:
        with self.Session() as session:
            print(f"get_card:user_id:{user_id}")
            statement = select(Player).where(Player.user_id == user_id)
            player = session.execute(statement).scalars().first()
            if player:
                return player
            return Player(user_id=123456, skills='')

    def set_card(self, user_id: int, skills: str):
        with self.Session() as session:
            try:
                statement = select(Player).where(Player.user_id == user_id)
                player = session.execute(statement).scalars().one_or_none()
                if player:
                    player.skills = skills
                else:
                    player = Player(user_id=user_id, skills=skills)
                session.add(player)
                
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling set_card: {e}")

    def delete_card(self, user_id: int):
        with self.Session() as session:
            try:
                statement = select(Player).where(Player.user_id == user_id)
                player = session.execute(statement).scalars().one_or_none()
                if player:
                    session.delete(player)
                    session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling delete_card: {e}")
                return False


    '''
    Logs database
    '''

    def create_log(self, group_id: int, file_name: str):
        status = 0  # 0：失败，1：成功，2：记录已存在且开始，3：记录已存在且未开始, 4:已结束，确认是否要覆盖
        with self.Session() as session:
            try:
                groupLogTable = create_groupId_table(group_id)
                inspector = inspect(self.engine)
                if not inspector.has_table(groupLogTable.name):
                    metadata.create_all(self.engine, tables=[groupLogTable])

                logFileStatement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                logFile = session.execute(logFileStatement).scalars().one_or_none()
                if logFile:  # LOG已经存在
                    if logFile.del_flag:  # LOG被伦理删除
                        logFile.del_flag = False
                        logFile.end_flag = False
                        logFile.log_on = False
                        logFile.name = file_name
                        session.add(logFile)
                        session.commit()
                        self.clear_group_logs(group_id)
                        status = 1
                    elif logFile.end_flag:
                        global del_confirm_dict
                        if group_id in del_confirm_dict:
                            del_confirm_dict.remove(group_id)
                            logFile.del_flag = False
                            logFile.end_flag = False
                            logFile.log_on = False
                            logFile.name = file_name
                            session.add(logFile)
                            
                            session.commit()
                            self.clear_group_logs(group_id)
                            status = 1
                        else:
                            del_confirm_dict.append(group_id)
                            file_name = logFile.name
                            status = 4 #4:已结束，确认是否要覆盖
                    else:  # LOG没有伦理删除
                        if logFile.log_on and not logFile.end_flag:  # LOG记录已经在进行中
                            file_name = logFile.name
                            status = 2  # 2：记录已存在且开始
                        else:  # LOG记录没有在进行中
                            file_name = logFile.name
                            status = 3  # 3：记录已存在且未开始
                else:
                    newLog = GroupLOG(group_id=group_id, name=file_name)
                    session.add(newLog)
                    session.commit()
                    status = 1
                return status, file_name
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling create_log: {e}")
                return status, None
            
    #获取logs状态
        
    #开始记录
    def open_log(self, group_id: int):
        status = 0 #0：失败，1：成功，2：记录已开始，3：记录不存在或结束
        with self.Session() as session:
            try:
                statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                log = session.execute(statement).scalars().one_or_none()
                if log:
                    if log.log_on:
                        status = 2
                    elif log.del_flag or log.end_flag:
                        status = 3
                    else:
                        log.end_flag = False
                        log.log_on = True
                        session.add(log)
                        
                        session.commit()
                        status = 1
                else:   
                    status = 3
                return status
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling open_log: {e}")
                return status

    #删除logs（伦理删除）
    def delete_log(self, group_id: int):
        with self.Session() as session:
            try:
                statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                log = session.execute(statement).scalars().one_or_none()
                if log:
                    log.del_flag = True
                    log.log_on = False
                    log.end_flag = True
                    session.add(log)
                    
                    session.commit()
                return True
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling delete_log: {e}")
                return False

    #LOG记录暂停
    def close_log(self, group_id: int):
        status = 0 #0：失败，1：成功，2：记录未开始，3：记录不存在或结束
        with self.Session() as session:
            try:
                statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                log = session.execute(statement).scalars().one_or_none()
                file_name = ""
                if log:
                    if not log.log_on:
                        status = 2
                    else:
                        if log.del_flag or log.end_flag:
                            status = 3
                        else:
                            file_name = log.name
                            log.end_flag = False
                            log.log_on = False
                            session.add(log)
                            
                            session.commit()
                            status = 1
                else:   
                    status = 3
                return status, file_name
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling close_log: {e}")
                return status, None

    #LOG记录结束
    def end_log(self, group_id: int):
        status = 0 #0：失败，1：成功，2：记录不存在
        fileName = ""
        with self.Session() as session:
            try:
                statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                log = session.execute(statement).scalars().one_or_none()
                if log:
                    if log.del_flag:
                        status = 2
                    else:
                        log.end_flag = True
                        log.log_on = False
                        session.add(log)
                        session.commit()
                        status = 1
                        fileName = log.name
                else:   
                    status = 2
                return status,fileName
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling end_log: {e}")
                return status,fileName
            
    #删除logs记录
    def clear_log(self, group_id: int):
        status = 0 #0：失败，1：成功，2：记录正在进行，3：记录不存在
        with self.Session() as session:
            try:
                statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
                log = session.execute(statement).scalars().one_or_none()
                if log:
                    if log.log_on:
                        status = 2
                    else:
                        table_name = f"GROUP_{group_id}_LOG"
                        with self.engine.begin() as connection:
                            connection.execute(text(f"DELETE FROM {table_name}"))
                        log.del_flag = True
                        log.end_flag = True
                        log.log_on = False
                        session.add(log)
                        session.commit()
                        status = 1
                else:   
                    status = 3
                return status
            except SQLAlchemyError as e:
                session.rollback()
                print(f"An error occurred while calling clear_log: {e}")
                return status
    
    def clear_group_logs(self, group_id: int):
        try:
            table_name = f"GROUP_{group_id}_LOG"
            with self.engine.begin() as connection:
                connection.execute(text(f"DELETE FROM {table_name}"))
        except SQLAlchemyError as e:
            print(f"An error occurred while calling clear_group_logs: {e}")

    
    #LOG是否记录中
    #  记录中->True 未记录&LOG不存在->False
    def is_logging(self, group_id: int) -> bool:
        with self.Session() as session:
            statement = select(GroupLOG.log_on).where(GroupLOG.group_id == group_id)
            logOnFlg = session.execute(statement).scalars().one_or_none()
            if logOnFlg:
                return logOnFlg
            return False
    
    #记录log
    def log_add(self, group_id: int, log_contents: LogContents):
        with self.engine.begin() as connection:
            try:
                table_name = f"GROUP_{group_id}_LOG"
                # groupLog = get_group_log_class(self.engine, table_name)
                # __init__(self, u_id, u_name, msg, comment_flg, time, del_flag, msg_id)
                u_id = log_contents.u_id
                u_name = log_contents.u_name
                # p_name = log_contents.p_name  # 未实装
                msg = log_contents.msg
                comment_flg = log_contents.comment_flg
                time = log_contents.time
                # u_cls = log_contents.u_cls  # 未实装
                del_flag = False
                msg_id = log_contents.msg_id
                sql_text = f"INSERT INTO {table_name} (u_id, u_name, msg, comment_flg, time, msg_id) VALUES ({u_id}, '{u_name}', '{msg}', {comment_flg}, '{time}', {msg_id})"
                connection.execute(text(sql_text))
            except SQLAlchemyError as e:
                print(f"An error occurred while calling log_add: {e}")
    # 撤回log记录
    def recall_log(self, group_id: int, message_id: int):
        with self.engine.begin() as connection:
            try:
                table_name = f"GROUP_{group_id}_LOG"
                sql_text = f"UPDATE {table_name} SET del_flag = 1 WHERE msg_id = {message_id}"
                connection.execute(text(sql_text))
                print("撤回了一条消息")
            except SQLAlchemyError as e:
                print(f"An error occurred while calling recall_log: {e}")
            
    
    # 导出logs用
    def get_log(self, group_id: int):
        with self.Session() as session:
            statement = select(GroupLOG).where(GroupLOG.group_id == group_id)
            log = session.execute(statement).scalars().one_or_none()
            log_name = ""
            if log:
                 log_name = f"{log.name}({str(group_id)}).xlsx"
            else:
                return None
        excel_absolute_path = os.path.join(os.getcwd(),"excel")
        if not os.path.exists(excel_absolute_path):
            os.makedirs(excel_absolute_path)
        output_path = os.path.join(excel_absolute_path, log_name)
        table_name = f"GROUP_{group_id}_LOG"
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, self.engine)
        # 将数据保存到Excel表格中
        df.to_excel(output_path, index=False)
        return log_name, output_path
        
    #初期化获取已经在记录logs的群列表
    def get_log_on_list(self) -> list:
        with self.Session() as session:
            statement = select(GroupLOG.group_id).where(GroupLOG.log_on == True)
            result_list = session.execute(statement).scalars().all()
            return result_list

