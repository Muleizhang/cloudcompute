# 云计算技术期末实验说明

## 1. 实验内容

部署 openGauss / GaussDB，并完成前后端分离 Web 应用的开发与部署。

## 2. 实验要求

1. 采用容器化技术，在华为云开发者空间部署伪分布式 openGauss / GaussDB 数据库服务。
2. 使用 Java 或 Python 开发前后端分离的 Web 应用，应用需具备完整的功能与界面。
3. Web 应用前端界面可以相对简单，但必须完整；每个前端 UI 元素都应有对应的后台处理逻辑。
4. Web 应用后端代码需要支持对 openGauss / GaussDB 数据库的读写操作。
   - 建议优先使用 Spark、Flink 等大数据处理框架对 openGauss / GaussDB 进行读写。
5. Web 应用前端和后端都需要通过 Dockerfile 制作成容器镜像，并在华为云开发者空间中完成容器化部署与测试。
6. 总结并整理项目配置、使用步骤和实验过程，撰写实验报告。

## 3. 检查与提交形式

1. 线下检查时间：2026 年 6 月 14 日至 2026 年 6 月 18 日之间，具体时间和地点另行通知。
2. 检查后需修改实验报告电子版，报告应包含关键实验步骤、演示过程和结果。
3. 提交材料应包含：
   - 实验报告
   - 源代码
   - 配置文件
   - 部署说明文档
   - 其他必要材料
4. 提交压缩包命名格式：`班级+姓名+学号`
5. 提交邮箱：`37737892@qq.com`
6. 截止时间：2026 年 6 月 20 日 23:59:59

## 4. 参考资料

### 4.1 使用源代码方式部署 GaussDB

- <https://www.cnblogs.com/jerrywang1983/articles/18846076>
- <https://blog.csdn.net/weixin_42350014/article/details/148363795>
- <https://support.huawei.com/enterprise/zh/doc/EDOC1100370291?idPath=22658044%7C22662728>
- <https://devstation.connect.huaweicloud.com/space/devportal/casecenter/ca5633bc6cd64657b11a416032653a1e/1>

### 4.2 使用 Docker 部署 GaussDB

- <https://www.cnblogs.com/lvjinlin/p/18747389>

### 4.3 使用 Docker 打包并部署应用

- Java 应用打包：<https://blog.csdn.net/qq_45637260/article/details/130325344>
- Python 应用打包：<https://www.jb51.net/server/30524788n.htm>

## 5. 实验报告格式

```text
《大数据与云计算技术》

本科生课程实验报告

题目：
专业：
班级：
姓名：
学号：

武汉大学计算机学院
年  月  日
```

## 6. 实验报告目录建议

```text
目 录

1 概述
1.1 课程选题背景（或需求分析）
1.2 课程实验内容

2 系统设计与实现
2.1 系统架构设计
2.2 系统技术选型
2.3 功能模块设计与实现

3 应用部署（章节小标题自拟）
3.1 部署 openGauss / GaussDB
3.2 部署前端 / 后端应用

4 测试评估（章节小标题自拟）

5 总结
5.1 项目开发的挑战与应对方法
5.2 项目部署存在的问题与不足
5.3 项目展望与学习心得

参考文献
```
