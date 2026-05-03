import time
import logging
import src.calc.generatable as g

from rich.table import Table
from fractions import Fraction

from src.app import App
from src.config import CONFIG
from src.calc.node import Node


class StopWatch():
    def __init__(self, duration: int = 60):
        self.mode: str = "StopWatch"
        
        self.input_error = False
        self.questions: list[dict[str, Node | Fraction]] = []
        self.total_score = 0
        self.gained_score = 0
        self.question = g.generate(CONFIG["question_max_score"])

        self.end_time = time.time() + duration

        self.app = App(self.build_frame)
        self.main()

    def get_input(self) -> Fraction:
        while True:
            try:
                user_input = self.app.input()
                if(len(user_input.strip()) == 0):
                    user_input = "0"
                result = Fraction(user_input)
            except:
                self.input_error = True
            else:
                self.input_error = False
                return result
        

    def main(self):
        while time.time() < self.end_time:
            #! 输入应正确处理
            user_ans = self.get_input()
            if(time.time() >= self.end_time):
                logging.info("Stopwatch timeout")
                break
            self.questions.append({
                "question": self.question,
                "user_answer": user_ans
            })
            score = self.question.score()
            logging.warning(f"question: {self.question}")
            logging.warning(f"user_ans: {user_ans}")
            logging.warning(f"correct ans: {self.question.get_value()}")
            logging.warning(f"is correct: {user_ans == self.question.get_value()}")
            if user_ans == self.question.get_value():
                self.gained_score += score
            self.total_score += score
            self.question = g.generate(CONFIG["question_max_score"])
        self.app.stop()

    def build_frame(self):
        remaining_time = int(self.end_time - time.time())
        if(remaining_time > 0):
            percentage = 0 if self.total_score == 0 else round(self.gained_score / self.total_score, 4) * 100

            grid = Table.grid()
            grid.add_column()
            grid.add_row(f"Mode: {self.mode}")
            grid.add_row(f"Percentage: {percentage}%")
            grid.add_row(f"Remaining Time: {remaining_time}s")
            grid.add_row("")
            grid.add_row(f"{str(self.question)} = USERINPUT")
            if(self.input_error):
                grid.add_row(f"Please input a valid number!")

            return grid
        else:
            percentage = 0 if self.total_score == 0 else round(self.gained_score / self.total_score, 4) * 100
            grid = Table.grid()
            grid.add_column()
            grid.add_row(f"Score: {self.gained_score}/{self.total_score}")
            grid.add_row(f"Percentage: {percentage}%")
            grid.add_row("已超时，按Enter退出。USERINPUT")
            return grid
