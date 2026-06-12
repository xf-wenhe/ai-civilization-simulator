# 讯飞API配置说明

## 正确的配置参数

根据你提供的讯飞Claude配置：

### 环境变量
```bash
ANTHROPIC_API_KEY=0a70901f2bd776bd7403dc5ff3f17eeb:NDhjNDAwYzRkNWM4ZWRmYTNiNmE0ZTNl
ANTHROPIC_BASE_URL=https://maas-coding-api.cn-huabei-1.xf-yun.com/anthropic
ANTHROPIC_MODEL=astron-code-latest
USE_SIMULATION=false
```

### 可用的模型名称
根据配置，讯飞支持：
- `astron-code-latest[1M]` - 带1M token限制
- `astron-code-latest` - 默认版本

---

## 如果仍然报错

### 方案1：尝试不同的模型名称

编辑 `backend/.env`：
```bash
# 尝试带token限制的版本
ANTHROPIC_MODEL=astron-code-latest[1M]
```

### 方案2：使用模拟模式

如果API仍有问题，可以继续使用模拟模式：
```bash
USE_SIMULATION=true
```

模拟模式也能完美运行，智能体基于性格做出决策！

---

## 启动项目

```bash
./final_run.sh
```