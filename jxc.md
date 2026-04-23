# 系统名称：进销存系统
是一款专业的、面向中小企业及个体商户的进销存管理软件,通过采购管理、销售管理、仓库管理、应收应付，快速的完成日常管理中的进货、出货、存货等操作，并结合高效的、准确的查询统计分析，让经营管理者们轻松的管帐，清楚的了解往来账款、销售状况、库存数量。

# AI coding：
1、【我】按模块，进行需求设计。
2、【AI Agent】把我把我的设计，转换为更加复杂的设计明细。
3、【AI Agent】按照设计明细，生成数据库的设计。
4、【AI Agent】按照设计明细，生成后端的代码和接口；并进行编译验证，接口模拟测试。
5、【AI Agent】设计设计明细，生成前端的代码和效果；验证前端的编译。
6、【我】验证AI的效果；发现BUG，让【AI Agent】进行 Debug。

# 目录介绍
design: 设计文档；MD文件所在目录。
pg: 数据初始化脚本存放目录；数据库创建标的等操作。
server: 后端代码目录；采用python Flask。
client: 前端代码目录；采用vue 3.0。
tools: AI生成代码的MD。

# 远程数据库
```
psql -U myuser -d postgres -h 127.0.0.1 -p 5432 -W
密码: yearlay_1987
```

# 后端重启命令
FLASK_DEBUG=false python3 server/jxcServer/app.py

# 前端重启命令
cd client/jxcClient && npm run dev
