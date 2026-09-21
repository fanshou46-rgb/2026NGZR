# src1.3 与 src1.3.1 测试协议

- 数据集：`题目/realcompetiton_2024/01.xml`–`36.xml`。
- 环境：WSL Ubuntu-18.04，SDK `/home/yifan/env-release-2026`。
- 模式：IT；02 为 Stage 1，其余为 Stage 2，与之前 realcompetition 比较一致。
- 时间：cserver 单题硬时限 5000 ms；src1.3.1 使用程序默认 4700 ms deadline 与 300 ms safety margin。
- 重复：每版两轮，共 144 次运行，以减弱 Stage 2 随机问答的偶然影响。
- 官方分：读取 cserver 的 `# Score`，并按平台规则封顶到 1000；同时保留原始分。
- 终态：从官方 `vanswer.txt` 统计最终 goal 与 constraint，客户端计数不替代官方终态。
- 执行逻辑：从 `server.log` 提取动作序列，比较动作数、共同前缀和首次分歧；另统计 src1.3.1 的 3A stop-gate/final 日志。
