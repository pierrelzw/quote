# Git Hooks 使用说明

本项目配置了完善的 Git 钩子来确保代码质量。

## Pre-commit 钩子

### 🔄 完整测试模式（默认）
```bash
git commit -m "Your commit message"
```

运行完整测试套件（约15-30秒）：
- ✅ Python 语法检查
- ✅ 模块导入验证
- ✅ 数据库功能测试（4项）
- ✅ 核心 API 测试（6项）
- ✅ 安全验证测试（4项）
- ✅ 基础性能测试（3项）
- ✅ 边界情况测试（4项）

### ⚡ 快速模式
```bash
QUICK_COMMIT=1 git commit -m "Quick fix"
```

运行最小检查（约2-5秒）：
- ✅ Python 语法检查
- ✅ 模块导入验证
- ✅ 基本 API 测试（1项）

## 手动运行测试

### 完整测试套件
```bash
cd backend-python
./run_tests.sh all
```

### 特定测试类型
```bash
./run_tests.sh unit        # 单元测试
./run_tests.sh integration # 集成测试
./run_tests.sh security    # 安全测试
./run_tests.sh performance # 性能测试
./run_tests.sh quick       # 快速测试
```

## 跳过钩子（不推荐）
```bash
git commit --no-verify -m "Skip hooks"
```

## 建议
- 日常开发：使用完整模式确保代码质量
- 紧急修复：使用快速模式快速提交
- 重要功能：手动运行完整测试套件

## 故障排除
如果测试失败：
1. 查看具体错误信息
2. 修复代码问题
3. 重新提交
4. 或使用 `--no-verify` 跳过（仅紧急情况）
# Git hooks guide added
