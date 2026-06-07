"""启动慧渔先知 Web 服务"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8081,
        reload=False,
    )
