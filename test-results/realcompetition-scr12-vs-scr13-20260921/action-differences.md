# 执行步骤差异

## 01 / 第 1 轮

- 1.2：36 步；1.3：38 步。
- `insert`：1.2[37:36] → 1.3[37:38]
  - 1.3：`Move 1|true → PutDown 15|true`

## 01 / 第 2 轮

- 1.2：0 步；1.3：38 步。
- `insert`：1.2[1:0] → 1.3[1:38]
  - 1.3：`PutDown 24|true → AskLoc 25| → AskLoc 25| → PickUp 6|true → Sense|6 1 24 → PutDown 6|true → Move 2|true → PickUp 7|true → Move 1|true → PutDown 7|true → Move 3|true → PickUp 8|true → Move 1|true → PutDown 8|true → Move 4|true → PickUp 9|true → Move 1|true → PutDown 9|true → Move 5|true → PickUp 10|true → Move 1|true → PutDown 10|true → Move 6|true → PickUp 11|true → Move 1|true → PutDown 11|true → Move 7|true → PickUp 12|true → Move 1|true → PutDown 12|true → Move 8|true → PickUp 13|true → Move 1|true → PutDown 13|true → Move 9|true → PickUp 15|true → Move 1|true → PutDown 15|true`

## 06 / 第 1 轮

- 1.2：37 步；1.3：38 步。
- `replace`：1.2[4:6] → 1.3[4:9]
  - 1.2：`AskLoc 5|at(5,6) → Move 6|true → Sense|5 9`
  - 1.3：`AskLoc 5|at(5,7) → Move 7|true → Sense|17 16 15 14 13 12 9 → AskLoc 5|at(5,4) → Move 4|true → Sense|6 7 8 10 11 9`
- `replace`：1.2[11:13] → 1.3[14:16]
  - 1.2：`AskLoc 23|at(23,8) → Move 8|true → PickUp 23|true`
  - 1.3：`AskLoc 23|at(23,1) → Move 1|true → PickUp 23|false`
- `replace`：1.2[15:16] → 1.3[18:18]
  - 1.2：`Sense|2 24 23 → PutDown 23|true`
  - 1.3：`PickUp 22|false`
- `insert`：1.2[21:20] → 1.3[23:23]
  - 1.3：`Sense|24 2 22`
- `replace`：1.2[22:26] → 1.3[25:26]
  - 1.2：`AskLoc 21|at(21,8) → Move 8|true → PickUp 21|true → Move 3|true → PutDown 21|true`
  - 1.3：`AskLoc 21|not_known → AskLoc 21|not_known`
- `replace`：1.2[37:37] → 1.3[37:38]
  - 1.2：`AskLoc 18|at(18,8)`
  - 1.3：`AskLoc 18|at(18,4) → Move 4|true`

## 06 / 第 2 轮

- 1.2：38 步；1.3：36 步。
- `insert`：1.2[4:3] → 1.3[4:6]
  - 1.3：`AskLoc 5|at(5,8) → Move 8|true → Sense|23 22 21 20 19 18 9`
- `delete`：1.2[8:10] → 1.3[11:10]
  - 1.2：`Move 3|true → PickUp 23|false → AskLoc 23|at(23,8)`
- `replace`：1.2[16:19] → 1.3[16:19]
  - 1.2：`AskLoc 22|at(22,7) → Move 7|true → PickUp 22|false → AskLoc 21|at(21,8)`
  - 1.3：`Move 8|true → PickUp 22|true → Move 3|true → PutDown 22|true`
- `replace`：1.2[24:26] → 1.3[24:27]
  - 1.2：`AskLoc 20|at(20,3) → PickUp 20|false → AskLoc 19|at(19,8)`
  - 1.3：`Move 8|true → PickUp 20|true → Move 3|true → PutDown 20|true`
- `replace`：1.2[31:33] → 1.3[32:35]
  - 1.2：`AskLoc 18|at(18,7) → Move 7|true → PickUp 18|false`
  - 1.3：`Move 8|true → PickUp 18|true → Move 3|true → PutDown 18|true`
- `delete`：1.2[35:38] → 1.3[37:36]
  - 1.2：`PickUp 11|true → Move 6|true → PutDown 11|true → Move 4|true`

## 07 / 第 1 轮

- 1.2：34 步；1.3：36 步。
- `replace`：1.2[4:6] → 1.3[4:9]
  - 1.2：`AskLoc 5|at(5,3) → Move 3|true → Sense|2 6`
  - 1.3：`AskLoc 5|at(5,1) → Move 1|true → Sense|1 6 → AskLoc 5|at(5,2) → Move 2|true → Sense|3 6`
- `delete`：1.2[8:9] → 1.3[11:10]
  - 1.2：`Move 6|true → Sense|5 6`
- `insert`：1.2[14:13] → 1.3[15:15]
  - 1.3：`Sense|5 7`

## 07 / 第 2 轮

- 1.2：34 步；1.3：31 步。
- `delete`：1.2[4:6] → 1.3[4:3]
  - 1.2：`AskLoc 5|at(5,1) → Move 1|true → Sense|1 6`

## 08 / 第 1 轮

- 1.2：33 步；1.3：30 步。
- `insert`：1.2[12:11] → 1.3[12:25]
  - 1.3：`AskLoc 8|at(8,7) → Move 7|true → PickUp 8|false → AskLoc 10|at(10,6) → Move 6|true → PickUp 10|false → AskLoc 9|at(9,7) → Move 7|true → PickUp 9|true → Move 6|true → PutDown 9|true → AskLoc 10|at(10,1) → Move 1|true → PickUp 10|false`
- `insert`：1.2[15:14] → 1.3[29:29]
  - 1.3：`PutDown 8|true`
- `delete`：1.2[16:33] → 1.3[31:30]
  - 1.2：`PutDown 8|true → AskLoc 10|not_known → AskLoc 10|at(10,7) → Move 7|true → PickUp 10|true → Move 6|true → PutDown 10|true → AskLoc 9|inside(9,14) → Move 7|true → Open 14|true → TakeOut 9 14|false → Sense|14 9 → TakeOut 9 14|false → Sense|14 9 → AskLoc 9|at(9,5) → Move 5|true → PickUp 9|false → Move 6|true`

## 08 / 第 2 轮

- 1.2：30 步；1.3：40 步。
- `replace`：1.2[4:6] → 1.3[4:10]
  - 1.2：`AskLoc 5|at(5,6) → Move 6|true → Sense|5 12 11 6`
  - 1.3：`AskLoc 5|at(5,1) → Move 1|true → Sense|1 6 → AskLoc 5|at(5,7) → Move 7|true → Sense|14 9 10 6 → AskLoc 5|at(5,3)`
- `insert`：1.2[10:9] → 1.3[14:23]
  - 1.3：`Move 3|true → Sense|2 8 7 → AskLoc 5|at(5,7) → Move 7|true → Sense|6 10 9 14 7 → AskLoc 5|at(5,1) → Move 1|true → Sense|1 7 → AskLoc 5|at(5,2) → PutDown 7|true`
- `replace`：1.2[11:12] → 1.3[25:31]
  - 1.2：`PutDown 7|true → AskLoc 8|at(8,3)`
  - 1.3：`PickUp 11|true → Move 2|true → Sense|3 11 → AskLoc 5|at(5,6) → Move 6|true → Sense|5 12 11 → PutDown 11|true`
- `delete`：1.2[17:26] → 1.3[36:35]
  - 1.2：`AskLoc 10|at(10,2) → Move 2|true → PickUp 10|false → AskLoc 9|not_known → AskLoc 9|at(9,7) → Move 7|true → PickUp 9|true → Move 6|true → PutDown 9|true → AskLoc 10|at(10,7)`
- `insert`：1.2[29:28] → 1.3[38:38]
  - 1.3：`Move 6|true`
- `replace`：1.2[30:30] → 1.3[40:40]
  - 1.2：`Move 6|true`
  - 1.3：`Move 7|true`

## 11 / 第 2 轮

- 1.2：38 步；1.3：37 步。
- `delete`：1.2[38:38] → 1.3[38:37]
  - 1.2：`Move 7|true`

## 13 / 第 1 轮

- 1.2：9 步；1.3：6 步。
- `delete`：1.2[7:9] → 1.3[7:6]
  - 1.2：`Move 1|false → AskLoc 4|at(4,2) → Sense|3 4 1 2`

## 13 / 第 2 轮

- 1.2：10 步；1.3：7 步。
- `insert`：1.2[5:4] → 1.3[5:5]
  - 1.3：`AskLoc 5|not_known`
- `delete`：1.2[7:10] → 1.3[8:7]
  - 1.2：`Move 1|false → AskLoc 4|not_known → AskLoc 4|at(4,2) → Sense|3 4 1 2`

## 14 / 第 1 轮

- 1.2：19 步；1.3：17 步。
- `replace`：1.2[3:3] → 1.3[3:5]
  - 1.2：`AskLoc 19|at(19,3)`
  - 1.3：`AskLoc 19|inside(19,12) → Move 12|true → TakeOut 19 12|true`
- `replace`：1.2[5:11] → 1.3[7:10]
  - 1.2：`PickUp 19|false → AskLoc 21|at(21,2) → Move 2|true → PickUp 21|true → Move 1|true → Sense|1 21 17 → PutDown 21|true`
  - 1.3：`Sense|3 20 16 19 17 → PutDown 19|true → AskLoc 21|not_known → AskLoc 21|not_known`
- `replace`：1.2[15:17] → 1.3[14:15]
  - 1.2：`AskLoc 16|at(16,8) → Move 8|true → PickUp 16|false`
  - 1.3：`Move 3|true → PickUp 16|true`
- `replace`：1.2[19:19] → 1.3[17:17]
  - 1.2：`Sense|15 10 17`
  - 1.3：`Sense|15 10 16 17`

## 14 / 第 2 轮

- 1.2：21 步；1.3：18 步。
- `replace`：1.2[9:14] → 1.3[9:11]
  - 1.2：`AskLoc 21|at(21,2) → Move 2|true → PickUp 21|true → Move 1|true → Sense|1 21 17 → PutDown 21|true`
  - 1.3：`AskLoc 21|at(21,4) → Move 4|true → PickUp 21|false`
- `replace`：1.2[21:21] → 1.3[18:18]
  - 1.2：`Sense|15 10 16 17`
  - 1.3：`Sense|10 15 16 17`

## 15 / 第 1 轮

- 1.2：20 步；1.3：24 步。
- `replace`：1.2[2:2] → 1.3[2:11]
  - 1.2：`AskLoc 11|at(11,1)`
  - 1.3：`AskLoc 11|at(11,5) → Move 5|true → PickUp 11|true → Move 7|true → PutDown 11|true → Open 7|true → PickUp 11|true → PutIn 11 7|true → AskLoc 19|not_known → AskLoc 19|at(19,1)`
- `delete`：1.2[4:6] → 1.3[13:12]
  - 1.2：`PickUp 11|false → AskLoc 19|at(19,6) → Move 6|true`
- `delete`：1.2[15:15] → 1.3[21:20]
  - 1.2：`AskLoc 18|not_known`
- `delete`：1.2[18:18] → 1.3[23:22]
  - 1.2：`Open 7|true`

## 16 / 第 1 轮

- 1.2：13 步；1.3：6 步。
- `replace`：1.2[4:7] → 1.3[4:5]
  - 1.2：`AskLoc 9|at(9,11) → Move 11|false → AskLoc 9|at(9,11) → Move 11|false`
  - 1.3：`AskLoc 9|at(9,22) → Sense|17 18 19 26 27 25 21 22 23 24 20 16 3 4 5 6 7 8 9 12 13 14 10 11 15 2`
- `delete`：1.2[9:13] → 1.3[7:6]
  - 1.2：`Move 11|false → AskLoc 13|at(13,11) → Move 11|false → PickUp 18|true → PutDown 18|true`

## 18 / 第 1 轮

- 1.2：17 步；1.3：16 步。
- `delete`：1.2[2:2] → 1.3[2:1]
  - 1.2：`AskLoc 26|not_known`

## 19 / 第 2 轮

- 1.2：38 步；1.3：37 步。
- `delete`：1.2[38:38] → 1.3[38:37]
  - 1.2：`Move 8|true`

## 20 / 第 2 轮

- 1.2：0 步；1.3：37 步。
- `insert`：1.2[1:0] → 1.3[1:37]
  - 1.3：`Move 3|true → PickUp 3|true → PutDown 3|true → PickUp 18|true → PutDown 18|true → Move 4|true → PickUp 2|true → Move 3|true → PutDown 2|true → Move 15|true → PickUp 4|true → Move 3|true → PutDown 4|true → Move 12|true → PickUp 5|true → Move 3|true → PutDown 5|true → Move 11|true → PickUp 6|true → Move 3|true → PutDown 6|true → Move 10|true → PickUp 7|true → Move 3|true → PutDown 7|true → Move 9|true → PickUp 8|true → Move 3|true → PutDown 8|true → Move 8|true → PickUp 9|true → Move 3|true → PutDown 9|true → Move 7|true → PickUp 10|true → Move 3|true → PutDown 10|true`

## 21 / 第 1 轮

- 1.2：0 步；1.3：38 步。
- `insert`：1.2[1:0] → 1.3[1:38]
  - 1.3：`Move 9|true → PickUp 8|true → Move 8|true → Sense|12 9 8 → PutDown 8|true → Move 9|true → PickUp 13|true → Move 8|true → PutDown 13|true → Move 15|true → PickUp 2|true → Move 8|true → PutDown 2|true → Move 14|true → PickUp 3|true → Move 8|true → PutDown 3|true → Move 13|true → PickUp 4|true → Move 8|true → PutDown 4|true → Move 12|true → PickUp 5|true → Move 8|true → PutDown 5|true → Move 11|true → PickUp 6|true → Move 8|true → PutDown 6|true → Move 10|true → PickUp 7|true → Move 8|true → PutDown 7|true → Move 7|true → PickUp 10|true → Move 8|true → PutDown 10|true → Move 7|true`

## 22 / 第 1 轮

- 1.2：35 步；1.3：34 步。
- `replace`：1.2[4:5] → 1.3[4:4]
  - 1.2：`AskLoc 5|at(5,4) → AskLoc 5|at(5,4)`
  - 1.3：`AskLoc 5|not_known`

## 23 / 第 2 轮

- 1.2：37 步；1.3：33 步。
- `delete`：1.2[4:7] → 1.3[4:3]
  - 1.2：`AskLoc 5|at(5,4) → AskLoc 5|at(5,3) → Move 3|true → Sense|2 11`

## 24 / 第 1 轮

- 1.2：34 步；1.3：36 步。
- `replace`：1.2[4:4] → 1.3[4:6]
  - 1.2：`AskLoc 5|not_known`
  - 1.3：`AskLoc 5|at(5,1) → Move 1|true → Sense|1 11`

## 24 / 第 2 轮

- 1.2：33 步；1.3：0 步。
- `delete`：1.2[1:33] → 1.3[1:0]
  - 1.2：`Move 4|true → PickUp 11|true → Sense|11 6 7 8 9 10 12 13 → AskLoc 5|at(5,6) → Move 6|true → Sense|5 11 → PutDown 11|true → Move 4|true → PickUp 9|true → Move 6|true → PutDown 9|true → Move 4|true → PickUp 10|true → Move 6|true → PutDown 10|true → Move 4|true → PickUp 6|true → Move 6|true → PutDown 6|true → Move 4|true → PickUp 12|true → Move 6|true → PutDown 12|true → Move 4|true → PickUp 7|true → Move 6|true → PutDown 7|true → Move 4|true → PickUp 8|true → Move 6|true → PutDown 8|true → Move 3|true → Sense|2`

## 28 / 第 1 轮

- 1.2：38 步；1.3：39 步。
- `insert`：1.2[39:38] → 1.3[39:39]
  - 1.3：`PickUp 12|true`

## 29 / 第 1 轮

- 1.2：36 步；1.3：38 步。
- `insert`：1.2[37:36] → 1.3[37:38]
  - 1.3：`PutDown 10|true → Move 15|true`

## 29 / 第 2 轮

- 1.2：36 步；1.3：38 步。
- `insert`：1.2[37:36] → 1.3[37:38]
  - 1.3：`PutDown 10|true → Move 15|true`

## 30 / 第 1 轮

- 1.2：36 步；1.3：38 步。
- `insert`：1.2[37:36] → 1.3[37:38]
  - 1.3：`PutDown 9|true → Move 8|true`

## 30 / 第 2 轮

- 1.2：36 步；1.3：38 步。
- `insert`：1.2[37:36] → 1.3[37:38]
  - 1.3：`PutDown 9|true → Move 8|true`

## 34 / 第 2 轮

- 1.2：38 步；1.3：35 步。
- `replace`：1.2[3:5] → 1.3[3:8]
  - 1.2：`AskLoc 17|at(17,3) → Move 3|true → PickUp 17|false`
  - 1.3：`AskLoc 17|inside(17,6) → Open 6|true → TakeOut 17 6|true → Move 2|true → Sense|2 17 → PutDown 17|true`
- `delete`：1.2[7:7] → 1.3[10:9]
  - 1.2：`Open 6|true`
- `delete`：1.2[10:10] → 1.3[12:11]
  - 1.2：`Sense|2 15`
- `delete`：1.2[20:24] → 1.3[21:20]
  - 1.2：`AskLoc 17|inside(17,6) → Move 6|true → TakeOut 17 6|true → Move 2|true → PutDown 17|true`
- `insert`：1.2[39:38] → 1.3[35:35]
  - 1.3：`Move 4|true`

## 35 / 第 1 轮

- 1.2：38 步；1.3：37 步。
- `delete`：1.2[7:9] → 1.3[7:6]
  - 1.2：`AskLoc 2|at(2,7) → Move 7|true → Sense|7 9 13 16 17`
- `insert`：1.2[39:38] → 1.3[36:37]
  - 1.3：`TakeOut 11 6|true → Move 4|true`

## 35 / 第 2 轮

- 1.2：0 步；1.3：37 步。
- `insert`：1.2[1:0] → 1.3[1:37]
  - 1.3：`Move 6|true → PickUp 17|false → AskLoc 17|inside(17,6) → Open 6|true → TakeOut 17 6|true → Move 9|false → AskLoc 2|at(2,10) → Move 10|true → Sense|2 17 → PutDown 17|true → Move 6|true → TakeOut 15 6|true → Move 10|true → PutDown 15|true → Move 8|true → PickUp 10|true → Move 6|true → PutIn 10 6|true → PickUp 12|true → Move 4|true → Sense|3 12 → PutDown 12|true → Move 8|true → PickUp 18|true → Move 10|true → PutDown 18|true → Move 7|true → PickUp 13|true → Move 10|true → PutDown 13|true → Move 6|true → TakeOut 14 6|true → Move 10|true → PutDown 14|true → Move 6|true → TakeOut 11 6|true → Move 4|true`

## 36 / 第 1 轮

- 1.2：39 步；1.3：37 步。
- `replace`：1.2[27:29] → 1.3[27:30]
  - 1.2：`AskLoc 14|at(14,8) → Move 8|true → PickUp 14|false`
  - 1.3：`AskLoc 14|inside(14,6) → TakeOut 14 6|true → Move 2|true → PutDown 14|true`
- `delete`：1.2[34:37] → 1.3[35:34]
  - 1.2：`AskLoc 14|at(14,3) → Move 3|true → PickUp 14|false → AskLoc 14|inside(14,6)`
- `replace`：1.2[39:39] → 1.3[36:37]
  - 1.2：`TakeOut 14 6|true`
  - 1.3：`TakeOut 11 6|true → Move 4|true`

## 36 / 第 2 轮

- 1.2：39 步；1.3：37 步。
- `delete`：1.2[21:23] → 1.3[21:20]
  - 1.2：`AskLoc 18|at(18,3) → Move 3|true → PickUp 18|false`
- `delete`：1.2[25:25] → 1.3[22:21]
  - 1.2：`Move 6|true`
- `insert`：1.2[40:39] → 1.3[36:37]
  - 1.3：`TakeOut 11 6|true → Move 4|true`

