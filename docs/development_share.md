# 开发历史与失败证据转发包

日期：2026-10-07。代码/历史材料快照为 `83e6a2259cd26eb82b5c5f1b4c8a086ef4f532c9`。ZIP位于D盘，不重新展开主工作区的旧版本，不修改比赛算法。

## 可直接转发

- 阅读包：`D:\RoboCupShare\development-failures-20261007\robocup-development-failures-review-20261007.zip`；34.80 MiB，7268个成员文件加清单。包含开发历史、失败索引、全部典型原记录、相关源码/测试/发布报告、逐题统计、题库、commit/diff、审计和复算脚本。
- 完整包：`D:\RoboCupShare\development-failures-20261007\robocup-development-failures-complete-20261007.zip`；1.587 GiB，7380个成员文件加清单。另加78份原开发证据ZIP、报告引用的旧版证据ZIP、两份比赛完整证据、29份补充归档ZIP和原发布ZIP。

只发送其中一个ZIP即可：一般讨论使用阅读包；需要审计全部原始记录或恢复完整运行矩阵时使用完整包。解压后从根README.md进入，文档链接使用包内相对路径。

两个包均含SOURCE_MANIFEST.json、逐文件SHA256及验证脚本；ZIP旁有整包.sha256文件。原评分/动作日志保持原字节，历史记录中的本机绝对路径保留作来源信息；接收者不依赖这些路径查看材料。

## 验证与边界

外层ZIP全部CRC、逐文件SHA256、成员数量、90个典型原始文件的来源哈希通过。递归报告链接共102个：阅读包96个文件直接提供、1个目录提供、5个大证据链接在完整包提供；完整包全部提供。独立解压副本的7268个文件SHA256通过，无需Git。原1.7.3报告的ROBOT_FLOW_1.9.md失效链接仅在转发副本修正为已重命名的ROBOT_FLOW_1.7.3.md，并注明修正。源码包含原版HistoryVersion/src1.6.7、200ms基线、比赛快照及1.7至1.7.7。具体收据见logs/development_share_20261007.json。

四组未提交概率草稿随包保存，并在README中明确为未完成研究。完整归档全部展开约16.42GiB，接收者可按前缀只恢复所需运行。重新生成正式分数需要接收者自己的官方SDK和Boost/C++环境；第三方SDK安装目录未打包。连续sanitizer检查仍为未完成。

工具入口：`python tools/package_development_share.py --output D:/RoboCupShare/新输出目录`。输出目录不得包含同名旧ZIP；工具不覆盖已有包。

阅读包SHA256：`a889d719c72279ee3dabe0d69c3f9d32bf35f7873bb66a52d30d8cb552176ba8`。

完整包SHA256：`6a2b75cefcfb50b433bb2ee044d76205b533b4362a4f3255e23470c32a633626`。
