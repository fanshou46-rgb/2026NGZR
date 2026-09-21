# scr1.3 版本说明

本目录以 `scr1.2` 为代码基线，修复 must-near 的关系构建、证据传播与运行时状态刷新。

- must-near/nextto 关系按对象 ID 对称构建，并覆盖多对象条件的 `X × Y`；
- `on` 不再误建为 must-near，位置 ID 也不再参与 must-near 对象矩阵扩容；
- 直接位置证据与 must-near 推导证据分开记录，冲突或 Sense 反证不会被强制覆盖；
- 感知、询问及原子动作改变位置后统一刷新 must-near 组件状态。

以下内容记录本项目最初导入的上游历史基线，仅用于追溯；其中哈希不是 scr1.3 当前文件哈希。

## Iron 临时基线

本目录由 2025 国赛 Stage2 候选包原样导入，尚未得到上届队员对“正式提交版本”的确认。

- 来源：`archive/legacy-2025/代码/stage2国赛/example(15).zip`
- ZIP SHA256：`dd1cad8aafe9f4bae4016236ece608f6436b964e08af97a4f2a180e8dccd8785`
- 导入日期：2026-08-25
- 预期 Git 标签：`legacy-stage2-2025`

在取得可运行、可计分的基线前，不应直接重写策略或大规模拆分 `rdfw.cpp`。任何与该目录的差异都必须能够通过 Git 和逐题回归解释。

## 文件哈希

```text
9ad5afc9d40e6e92341b7e38e1b8699f10e56ffad18cd41a2bc1fe7abf5df936  CMakeLists.txt
746b17d5c62ae2d3d8f1e300a849f1d019458eb11641cd48ecbc9bad113e1fc9  debuglog.hpp
adcf1e3b5e63d3f0d3bd798b5a5952227d8c6bef279215f32a03cefa22b9c187  main.cpp
ee0bf43aafa2be02c02362ee16f32bf3c8ad949fb3fcc4f7f646901b480e5936  parser.cpp
b6efd33040703d51483d6d303be9d1decde72f492275d1abe78ddbd2fd449887  parser.hpp
9d1d41367ff16871647fcc6bd95aa114fea197da5c3cd22435a611f6d39483e3  rdfw.cpp
5c29620a3b0846807c4edf5a6a9f5c53313c171e9440a7be1c61b7175c533397  rdfw.hpp
66f951c478092c11bf1e29894401401a55c0f26cfc4cf038acfeb1d6a8515a41  words.txt
```
