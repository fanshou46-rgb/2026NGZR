# 修复预览初始化之前的完整证据

这里保留第一份全部 284 对运行、全部下降案例、原始日志/官方终态，以及首次 sanitizer 日志。
该检查 143/145 通过，2 项 UBSan 失败定位到 `isMultiGotoMode` 未初始化的 bool 读取。
正式 Plan 已在调度前显式赋 false，问题由直接调用预览的测试暴露。

后续只在字段声明补默认 false，重新完成普通/SDK 与 sanitizer 验证，并对最终二进制完整配对。
两份配对分别统计，不用第二份替换这里的不利结果。最终交付统计见上级 REPORT.md。
初始化一行差异的审计见上级 initialization-patch-audit.json。

本目录 REPORT.md 是当时生成的调度比较结果，ASan 失败以 sanitizer-ctest.log 和本说明为准。
原始 SDK iclingo 在压缩证据中去重存储一次；全部运行日志、输入和 ASP 输出均保留。
