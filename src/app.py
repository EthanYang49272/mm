import os
import sys
import time
import threading
import logging
from queue import Queue
from rich.console import Console

from typing import Callable, Any

USER_INPUT_PLACEHOLDER = "USERINPUT"

class App:
    def __init__(self, build_frame: Callable[[], Any]):
        self.last_line_count = 0  # 追踪上一帧占用的物理行数
        self.build_frame = build_frame

        self.running = True
        self.input_text: str = ""
        self.history: Queue[str] = Queue()

        self.console = Console()

        # 渲染单独放在一个线程
        self.render_thread = threading.Thread(target=self.render, daemon=True)
        self.input_thread = threading.Thread(target=self.input_listener)
        self.render_thread.start()
        self.input_thread.start()
    
    def update_frame(self, new_build_frame: Callable[[], Any]):
        self.build_frame = new_build_frame

    def render(self):
        # 初始设置：隐藏硬件光标并预留显示空间
        total_lines = self.console.size.height
        sys.stdout.write(f"\033[?25l\033[{total_lines}F")
        sys.stdout.flush()

        try:
            while self.running:
                # 渲染这一帧
                with self.console.capture() as capture:
                    self.console.print(self.build_frame())
                
                # 适配换行符（Raw 模式关键）
                frame_str = capture.get().replace("\n", "\r\n")
                current_lines = frame_str.count("\r\n")

                # 显示用户正在输入的内容
                cursor = "█" if int(time.time() * 2) % 2 == 0 else " " #!
                frame_str = frame_str.replace(USER_INPUT_PLACEHOLDER, f"{self.input_text}{cursor}") #!

                # 原子化指令拼接：回退 + 清除 + 绘图
                output = ""
                if self.last_line_count > 0:
                    output += f"\033[{self.last_line_count+1}F" # 向上移动 N 行
                output += "\033[J"     # 清除从光标到屏幕末尾的内容
                output += frame_str    # 绘制新帧内容
                
                # 一次性写入，彻底杜绝闪烁
                sys.stdout.write(output)
                sys.stdout.flush()
                
                self.last_line_count = current_lines
                time.sleep(0.05) # 20 FPS 的刷新率

        finally:
            # 退出保护：显示光标并换行
            self.running = False
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()
            logging.info("Render stopped")

    def input_listener(self):
        if os.name == 'nt':  # Windows 逻辑
            import msvcrt
            while self.running:
                if msvcrt.kbhit():
                    try:
                        char = msvcrt.getch().decode('utf-8')
                        self.handle_char(char)
                    except: pass
                time.sleep(0.01)
        else:  # Unix (Mac/Linux) 逻辑 
            import tty, termios, select
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd) # 开启原始模式
                while self.running:
                    r, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if r:
                        char = sys.stdin.read(1)
                        self.handle_char(char)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        logging.info("Input stopped")

    def handle_char(self, char: str):
        logging.info("User pressed %s" % char)
        if char == '\x03': # Ctrl+C
            self.running = False
        elif char in ('\r', '\n'): # 回车
            self.history.put(self.input_text)
            self.input_text = ""
            logging.info("Enter Detected")
        elif char in ('\x7f', '\x08'): # 退格
            self.input_text = self.input_text[:-1]
        elif ord(char) >= 32: # 可打印字符
            self.input_text += char

    def input(self) -> str:
        logging.info("Waiting for user's input")
        result = self.history.get()
        logging.info("User's input returned")
        return result
        
    def stop(self):
        logging.info("App Stopping")
        self.running = False
        self.input_thread.join()
        self.render_thread.join()
        logging.info("App Stopped")
    
    def start(self):
        self.running = True
