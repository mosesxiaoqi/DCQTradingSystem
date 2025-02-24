import time
import json
import asyncio
import websockets
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.account_decoder import parse_token_account

# 配置参数
# Solana 主网 RPC 端点
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
# Raydium AMM 程序 ID
RAYDIUM_AMM_ID = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
# USDC mint 地址
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
# SOL mint 地址
SOL_MINT = "So11111111111111111111111111111111111111112"
# SOL/USDC 池地址（Raydium）
POOL_ADDRESS = "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"

async def get_token_price(token_mint_address):
    """获取代币实时价格"""
    try:
        # 初始化 Solana 客户端
        client = AsyncClient(SOLANA_RPC_URL)
        
        # 将代币 mint 地址转换为 PublicKey
        token_mint = Pubkey.from_string(token_mint_address)
        
        # 获取 Raydium 上相关的 liquidity pool
        async with websockets.connect("wss://api.mainnet-beta.solana.com") as websocket:
            # 订阅账户变化
            subscription_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "accountSubscribe",
                "params": [
                    str(token_mint),
                    {"encoding": "jsonParsed", "commitment": "processed"}
                ]
            }
            
            await websocket.send(json.dumps(subscription_request))
            
            # 接收初始订阅确认
            confirmation = await websocket.recv()
            print(f"订阅确认: {confirmation}")
            
            while True:
                # 接收实时更新
                update = await websocket.recv()
                data = json.loads(update)

                print(f"接收到更新: {data}")
                
                if "params" in data and "result" in data["params"]:
                    account_data = data["params"]["result"]["value"]["data"]
                    # 这里需要解析具体的 pool 数据来计算价格
                    # 实际应用中需要根据 pool 的结构来提取储备量
                    print(f"接收到账户更新: {account_data}")
                
                # 添加简单的价格计算逻辑（示例）
                # 实际需要从 pool 获取 SOL 和 token 的储备量
                # price = sol_reserve / token_reserve
                await asyncio.sleep(1)  # 控制更新频率
                
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        await client.close()

def monitor_token_price(token_mint_address):
    """运行价格监控"""
    print(f"开始监控代币: {token_mint_address}")
    asyncio.run(get_token_price(token_mint_address))

# 异步函数：监控 Raydium 池价格
async def monitor_raydium_price(pool_address):
    try:
        # 初始化 Solana 异步客户端
        client = AsyncClient(SOLANA_RPC_URL)
        # 将池地址转换为 Pubkey 对象
        pool_pubkey = Pubkey.from_string(pool_address)
        # 建立 WebSocket 连接
        async with websockets.connect("wss://api.mainnet-beta.solana.com") as websocket:
            # 构造订阅请求
            subscription_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "accountSubscribe",
                "params": [
                    str(pool_pubkey),
                    {"encoding": "base64", "commitment": "processed"}
                ]
            }
            # 发送订阅请求
            await websocket.send(json.dumps(subscription_request))
            # 接收订阅确认
            confirmation = await websocket.recv()
            print(f"订阅确认: {confirmation}")
            # 持续监听更新
            while True:
                # 接收账户更新
                update = await websocket.recv()
                data = json.loads(update)
                if "params" in data and "result" in data["params"]:
                    # 提取账户数据
                    account_data = data["params"]["result"]["value"]
                    lamports = account_data["lamports"]
                    raw_data = account_data["data"][0]
                    # 假设的储备量（需真实解析）
                    sol_reserve = 1000000000
                    token_reserve = 2000000000
                    # 计算价格（SOL/USDC）
                    price = sol_reserve / token_reserve * (10 ** 6)
                    # 输出时间戳（slot）
                    print(f"时间: {data['params']['result']['context']['slot']}")
                    # 输出 SOL 储备量
                    print(f"SOL 储备量: {sol_reserve / 10**9} SOL")
                    # 输出 USDC 储备量
                    print(f"USDC 储备量: {token_reserve / 10**6} USDC")
                    # 输出价格
                    print(f"价格: 1 USDC = {price:.6f} SOL")
                    print("---")
                # 控制更新频率
                await asyncio.sleep(0.5)
    # 处理异常
    except Exception as e:
        print(f"发生错误: {e}")
    # 关闭客户端
    finally:
        await client.close()

# 函数：启动价格监控
def start_monitoring(pool_address):
    print(f"开始监控 Raydium 池: {pool_address}")
    asyncio.run(monitor_raydium_price(pool_address))

# 主程序入口
if __name__ == "__main__":
    try:
        start_monitoring(POOL_ADDRESS)
    # 处理键盘中断
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    
    try:
        monitor_token_price(USDC_MINT)
    except KeyboardInterrupt:
        print("\n监控已停止")

    try:
        start_monitoring(POOL_ADDRESS)
    # 处理键盘中断
    except KeyboardInterrupt:
        print("\n监控已停止")
