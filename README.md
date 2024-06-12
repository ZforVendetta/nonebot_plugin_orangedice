<div align="center">

# NoneBot Plugin Orangedice

一个普通的COC骰子插件  
真的不点个Star吗？  
<a href="https://pypi.python.org/pypi/nonebot-plugin-orangedice">
    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-orangedice?style=for-the-badge" alt="Download">
</a>

</div>

## 修改内容
- 2024/05/13 ①帮助信息内容 ②上传群文件权限信息内容 ③.coc指令一次生成上限10条，且添加排除幸运数值总和以及全部数值总和 ④修改.ra指令鉴定为大于小于和小于等于 ⑤录入车卡信息显示玩家id以区分 ⑥完成TODO-LIST1~5项

- 2024/05/14 ①完成TODO-LIST6~8项 ②修改信息使投掷结果更直观

- 2024/05/16 修改模糊匹配（同义词匹配）的逻辑，并修正错误

- 2024/06/12 替换了python自己的random的方法通过secret库让投掷结果添加一点神秘加成（没什么用的更新），修改了数据库结构，重写了log记录逻辑。可导出excel文档，数据详尽，方便整理合并。仍有大量方法实现很简陋，等待日后完善。

## TODO-LIST（优先级从上到下）
- ~~。/.均可匹配指令~~
- ~~.ra50 此类消息的处理~~
- ~~.st show 力量 显示单个属性~~
- ~~.st hp -1d4 执行加减运算~~
- ~~.rd10 省略1~~
- ~~.rp 惩罚骰roll完之后，再roll一个1d10，两次的十位数取低~~
- ~~.rb 奖励骰roll完之后，再roll一个1d10，两次的十位数取高~~
- ~~.rc 标准规则书 1为大成功，100为大失败，如果该技能不足50，那么96-100是大失败~~
- ~~弃用sqlmodel更换sqlalchemy以实现分群动态建表之后的增删改查~~
- ~~修改log逻辑,数据库添加排他锁，添加错误回滚。~~

    ~~.log new [logName] 添加创建log指令并可命名log~~

    ~~log格式化log文本文件的记录内容（增加数据库记录的信息）~~

    ~~添加撤回操作删除log记录处理~~
- 疯狂的结果对应持续时间需要修改/重写
- 技能对抗,斗殴和反击
- 修改数据库结构以适配以下的特性
- 避免同用户多团同开的属性数据覆盖

    .new 希欧希一郎 创建角色

    .tag 希欧希一郎 别群绑定同一角色（秘密团/多团同时开）


## 可选配置

``` 
#version==0.2.0
CARD_FILE=card.json #人物卡文件位置
LOG_FILE=log.json #日志文件位置
CACHE_FILE=cache.json #缓存文件位置
```

```
#version>=0.3.0
CACHE_FILE=cache.txt # 缓存文件位置
SQLITE_FILE=DICE.db #数据库位置
```

## 指令集

- [x] .r  骰点
- [x] .rh 暗骰
- [x] .ra 属性检定骰点
- [x] .rb 属性奖励检定骰点
- [x] .rp 属性惩罚检定骰点
- [x] .rc 属性标准规则书检定骰点
- [x] .st 录卡/加减属性数值
- [x] .st show 显示指定属性数值
- [x] .li/ti 总结/临时疯狂检定
- [x] .sc sancheck
- [x] .log 日志
- [x] .log new 创建指定名称日志
- [x] .log on 开始记录日志
- [x] .log off 暂停记录日志
- [x] .log end 结束记录日志
- [x] .log upload 上传日志到群文件
- [x] .log clear 删除日志记录（逻辑删除）
- [ ] .new 创建角色
- [ ] .tag 绑定角色
- [x] .help 帮助
- [x] .list 疯狂列表
- [x] .coc 车卡
- [x] .en 成长检定
- [x] .dao 导出人物卡

---

### HELP 获取帮助（未更新）
获取快捷的指令帮助
```
.help

".r#expr(attr) 骰点"
".ra(attr)(value) 属性骰点"
".st(attr value)/clear 人物卡录入/清除"
".log on/off/upload/clear 日志功能开启/关闭/上传/清除"
".sc(success)/(failure) ([san]) 理智检定[不可使用除法]"
".rh 暗骰"
".show 展示人物卡"
".ti/li 临时/永久疯狂检定"
".coc(value) 生成coc人物卡"
".en[attr][expr] 属性成长"
```

### RD 普通骰子（未更新）
普通的骰点，格式为 [onedice标准](https://github.com/OlivOS-Team/onedice) 内COC的骰子格式

```
.r[expr]

.r1d100
.r5d100a10
```

### RA 属性掷点（未更新）
掷出一个 1D100 的骰子进行属性/技能检定  
不提供 value 则在人物卡中获取属性

```
.ra[attritube]([value])

.raStar50
.ra属性60
```

### RH 暗骰（未更新）
掷出一个 1D100 的骰子
并发送至指令执行者的窗口 
```
.rh
```

### EN 成长
对属性进行成长检定
会自动赋值到人物卡上
```
.en[attritube][expr]

.en力量20
.en理智1d5+2
```

### ST 录人物卡（未更新）
录入人物属性卡，仅当使用 clear 时重置人物卡
```
.st([attritube][value])/(clear)

.st测试10普通属性100san50..
.st clear
```

### SC 理智检定
进行 **san check** 检定，自动扣除人物卡内的 san。  
支持 **dice expr** 但不支持除法运算符。

```
.sc [success]/[failure] ([san])

.sc 1d8/1d3
```

### TI/LI 疯狂检定
获取一个临时/总结的疯狂发作症状
```
.li #随机获取疯狂发作-总结症状

.ti #随机获取疯狂发作-临时症状
```

### LIST 疯狂表
获取临时/总结疯狂表
```
.list temp/forever
```

### COC 车卡
基于COC7规则的属性随机生成
每次至多生成三个角色
```
.coc[times]

.coc3 #生成三个跑团角色属性卡
```

### LOG 日志记录（未更新）
记录跑团/群聊日志，此功能需群管理/群主才可开启
```
.log (on)/(off)/(upload)/(clear)

.log on     #开启日志记录功能
.log off    #暂停当前日志记录
.log upload #将日志记录上传至群文件
.log clear  #清空之前的日志
```

### DAO 导出角色卡
将角色卡导出来多次使用，与 SHOW 指令的区别为  
SHOW 指令会排除一些重复属性，而 DAO 则会把所有属性全部导出
```
.dao
```

## 相关与参考项目

- [onedice](https://github.com/OlivOS-Team/onedice): Today, we stand as one.
- [nonebot_plugin_cocdicer](https://github.com/abrahum/nonebot_plugin_cocdicer): A COC dice plugin for Nonebot2
- [dice!](https://github.com/Dice-Developer-Team/Dice): QQ Dice Robot For TRPG
- [Blog](https://ruslanspivak.com/lsbasi-part1/)
