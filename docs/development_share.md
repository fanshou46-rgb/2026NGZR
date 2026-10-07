# 开发历史与失败证据转发包

日期：2026-10-07。代码/历史材料快照为 `7f68f6478505e730ed7349c32507234818bee936`。ZIP位于D盘，不重新展开主工作区的旧版本，不修改比赛算法。

## 可直接转发

- 阅读包：`D:\RoboCupShare\development-failures-20261007\robocup-development-failures-review-20261007.zip`；33.12 MiB，7258个成员文件加清单。包含开发历史、失败索引、全部典型原记录、相关源码/测试/发布报告、逐题统计、题库、commit/diff、审计和复算脚本。
- 完整包：`D:\RoboCupShare\development-failures-20261007\robocup-development-failures-complete-20261007.zip`；1.548 GiB，7369个成员文件加清单。另加78份原开发证据ZIP、两份比赛完整证据、29份补充归档ZIP和原发布ZIP。

只发送其中一个ZIP即可：一般讨论使用阅读包；需要审计全部原始记录或恢复完整运行矩阵时使用完整包。解压后从根README.md进入，文档链接使用包内相对路径。

两个包均含SOURCE_MANIFEST.json、逐文件SHA256及验证脚本；ZIP旁有整包.sha256文件。原评分/动作日志保持原字节，历史记录中的本机绝对路径保留作来源信息；接收者不依赖这些路径查看材料。

## 验证与边界

外层ZIP全部CRC、逐文件SHA256、成员数量、90个典型原始文件的来源哈希通过。主要报告37个本地链接：阅读包34个直接提供、3个大证据链接在完整包提供；完整包全部提供。源码包含原版HistoryVersion/src1.6.7、200ms基线、比赛快照及1.7至1.7.7。具体收据见logs/development_share_20261007.json。

四组未提交概率草稿随包保存，并在README中明确为未完成研究。完整归档全部展开约16.42GiB，接收者可按前缀只恢复所需运行。重新生成正式分数需要接收者自己的官方SDK和Boost/C++环境；第三方SDK安装目录未打包。连续sanitizer检查仍为未完成。

工具入口：`python tools/package_development_share.py --output D:/RoboCupShare/新输出目录`。输出目录不得包含同名旧ZIP；工具不覆盖已有包。

阅读包SHA256：`7e2ee33d8d2f7588f78a4e17f2ee8d54b8e8dc74207e13c76fb7c7c8a1c33d42`。

完整包SHA256：`f96fd19602a576814e828649f38a7768193f6ccd74d427d85be873037517abee`。
