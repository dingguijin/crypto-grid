# crypto-grid / 加密货币网格自动交易
Crypto grid trade strategy and logging all trades in Odoo system

> 风险提示，加密货币交易是一个高风险领域，网格策略对于单边行情会有长时间的浮亏。本程序只是个人兴趣进行学习和研究，不构成任何投资建议。


本系统分成两部分，第一部分是程序化交易部分，另一部分是交易数据存储分析部分。

## 程序化交易

程序化交易是一个 Python 程序，通过 Supervisor 控制，它不断运行，对指定的标的进行网格化交易（挂单/MAKER）。目前支持 FTX 交易所。

## 交易数据存储分析

如果初次使用可以选择不使用交易数据存储分析，这个模块依赖 Odoo，需要安装 POSTGRES 数据库，启动 Odoo。

数据分析是一个可选的部分，这个部分能够把交易数据存储在数据库中，并且进行数据分析。比如分析每日交易次数，盈利情况等等。交易数据存储在 Odoo 系统中，是以一个 Odoo 的 Addon 提供。

使用数据存储分析需要安装 Odoo，并且加载这个插件。具体的使用安装方法见下文。

## 启动程序化交易


### 系统需求

* 国内用户科学上网，不然连不上各个交易所的 API
* Linux/Mac OS X Windows 没有测试过，原则上只要有 Python 3 即可

### 下载代码
并且切换目录到 trade 下面。安装一些需要的 Python 包。

```
    git clone https://github.com/dingguijin/crypto-grid.git
    cd crypto-grid/trade
    pip install -r requirments.txt
```

### 配置参数

#### 获取 FTX API 的 KEY 和 SECRET
将获取的 API KEY 和 SECRET 写入 .env 文件之中，.env 和 grid.py 在同一个目录。

千万不要将 API KEY/SECRET 泄漏。

```
FTX_API_KEY=""
FTX_API_SECRET=""
```

获取 FTX API KEY/SECRET 参见 [https://ftx.com/profile](https://ftx.com/profile)

### 配置 Supervisor 和 命令行参数

Supervisor 可以监控 Python 命令行的程序执行，如果程序遇到异常停止了，Supervisor 还可以将程序重新启动。

supervisord.conf 中已经写好了一个例子。

```
[program:grid-dgj-grt]
priority=1
numprocs=1
directory=/tmp
autostart=false
autorestart=true
redirect_stderr=true
process_name=%(program_name)s-%(process_num)02d
command=python /home/ubuntu/crypto-grid/trade/grid.py --exchange ftx --subaccount_name DGJ-01 --market GRT-PERP --step_ratio 0.0008 --size 250 --strategy_id 4
stdout_logfile=/usr/local/var/log/%(program_name)s.log
```

其中 priority 表示有很多个 program 的时候先启动哪个，保持默认的即可。

numprocs 设为 1 ，表示这个命令要启动几个，保持 1.

autostart 是指启动 supervisord 的时候是否自动启动该命令，保持 false。

autorestart 保持 true，指遇到异常停止后是否自动启动。

command 就是完整命令行。

```
其中 exchange 是指交易所，目前支持 ftx，正在尝试支持 dydx/bianace/mxc 等。

subaccount_name 是 ftx 交易所支持的子账户，如果没有为 subaccount name 指定参数就是主账户。

market 是指交易的品种，最好使用永续合约，这样可以不用提前建立底仓。

step_ratio 是指网格步子大小，0.0008 是指程序会在当前价格的 （1+0.0008）倍挂卖单，在（1-0.0008）倍挂买单。

size 是指每次交易量， 250 是指每次挂 250 个 GRT 的买卖单。

strategy_id 是指交易数据存储分析系统的 ID，如果不使用交易数据存储系统请给 -1。
```

如果暂时不想使用 Supervisor 管理程序运行，那么直接在 console 下执行 command 的命令行即可。

### 启动/停止/运行日志
启动 Supervisor

```
supervisord -c supervisord.conf
```

管理 Supervisor

```
supervisorctl -s http://localhost:9001

```

supervisorctl 执行成功后，可以执行 supervisor 的命令进行命令的查看，开始和停止。

```
> status

用 status 命令可以列出所有的 program，并检查状态。

> start program_name
> stop program_name
> restart program_name

program name 一般都是 group::program 组成。
如果按照上面的配置 program_name 可能是
grid-dgj-grid::grid-dgj-grid-00


```

## 启动交易数据存储分析

### 了解 Odoo

参见 [Odoo](https://odoo.com)。

### 下载代码

```
    git clone https://github.com/odoo/odoo.git
    git clone https://github.com/dingguijin/crypto-grid.git
    cd crypto-grid/analyse
    pip install -r requirments.txt

```


### 启动/停止/运行日志

```
../../odoo/odoo.bin -c odoo.config
```

## 讨论组

[DISCORD](https://discord.gg/7vcnEDAa)

[TWITTER](https://twitter.com/dingguijin)

## 赞助

ERC20 [DDING.ETH](0x211164B771F7910445E96914E7a4D66a406458d2) 

0x211164B771F7910445E96914E7a4D66a406458d2
