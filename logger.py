import sys

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout  # 保留原始终端输出
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):  # 确保缓冲区内容写入文件
        self.terminal.flush()
        self.log.flush()

# 重定向标准输出和错误输出
sys.stdout = Logger("output.log")
sys.stderr = sys.stdout  # 将错误输出也重定向到同一文件
