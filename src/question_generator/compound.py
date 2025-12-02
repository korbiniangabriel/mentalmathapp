"""Compound (multi-step) question generators."""
import random
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class CompoundGenerator(QuestionGenerator):
    """Generates multi-step compound questions."""
    
    @property
    def question_type(self) -> str:
        return "compound"
    
    @property
    def category(self) -> str:
        return "compound"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a compound question."""
        problem_types = ["percentage_operations", "arithmetic_chain", "profit_calculation"]
        p_type = random.choice(problem_types)
        
        if p_type == "percentage_operations":
            return self._generate_percentage_operations(difficulty)
        elif p_type == "arithmetic_chain":
            return self._generate_arithmetic_chain(difficulty)
        else:
            return self._generate_profit_calculation(difficulty)
    
    def _generate_percentage_operations(self, difficulty: str) -> Question:
        """Generate questions with multiple percentage operations."""
        start = random.randint(50, 300)
        
        if difficulty == "easy":
            increase_pct = random.choice([10, 20, 25, 50])
            decrease_pct = random.choice([10, 20, 25])
            
            after_increase = start * (1 + increase_pct / 100)
            final = after_increase * (1 - decrease_pct / 100)
            
            question_text = f"{start} increased by {increase_pct}%, then decreased by {decrease_pct}%"
        elif difficulty == "medium":
            pct1 = random.randint(10, 30)
            pct2 = random.randint(10, 30)
            operations = random.choice([("increased", "decreased"), ("decreased", "increased")])
            
            if operations[0] == "increased":
                temp = start * (1 + pct1 / 100)
            else:
                temp = start * (1 - pct1 / 100)
            
            if operations[1] == "increased":
                final = temp * (1 + pct2 / 100)
            else:
                final = temp * (1 - pct2 / 100)
            
            question_text = f"{start} {operations[0]} by {pct1}%, then {operations[1]} by {pct2}%"
        else:  # hard
            pct1 = random.randint(5, 25)
            pct2 = random.randint(5, 25)
            pct3 = random.randint(5, 20)
            
            temp1 = start * (1 + pct1 / 100)
            temp2 = temp1 * (1 - pct2 / 100)
            final = temp2 * (1 + pct3 / 100)
            
            question_text = f"{start} increased by {pct1}%, then decreased by {pct2}%, then increased by {pct3}%"
        
        answer = round(final, 2)
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=str(int(answer) if answer == int(answer) else answer),
            acceptable_answers=[str(int(answer)), str(round(answer, 1)), str(round(answer, 2))],
            metadata={"start_value": start, "type": "percentage_operations"}
        )
    
    def _generate_arithmetic_chain(self, difficulty: str) -> Question:
        """Generate arithmetic operation chains."""
        start = random.randint(10, 100)
        
        if difficulty == "easy":
            add = random.randint(10, 50)
            mult = random.randint(2, 5)
            sub = random.randint(10, 50)
            
            result = (start + add) * mult - sub
            question_text = f"Start with {start}, add {add}, multiply by {mult}, then subtract {sub}"
        elif difficulty == "medium":
            add = random.randint(20, 80)
            mult = random.randint(2, 7)
            div = random.choice([2, 3, 4, 5])
            sub = random.randint(10, 50)
            
            result = ((start + add) * mult) // div - sub
            question_text = f"Start with {start}, add {add}, multiply by {mult}, divide by {div}, then subtract {sub}"
        else:  # hard
            operations = [
                (random.randint(10, 50), "add"),
                (random.randint(2, 5), "multiply"),
                (random.randint(10, 30), "subtract"),
                (random.choice([2, 3, 4]), "divide"),
                (random.randint(5, 20), "add")
            ]
            
            result = start
            steps = [f"Start with {start}"]
            for value, op in operations:
                if op == "add":
                    result += value
                    steps.append(f"add {value}")
                elif op == "subtract":
                    result -= value
                    steps.append(f"subtract {value}")
                elif op == "multiply":
                    result *= value
                    steps.append(f"multiply by {value}")
                elif op == "divide":
                    result //= value
                    steps.append(f"divide by {value}")
            
            question_text = ", then ".join(steps)
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=str(int(result)),
            metadata={"start_value": start, "type": "arithmetic_chain"}
        )
    
    def _generate_profit_calculation(self, difficulty: str) -> Question:
        """Generate profit/loss calculation questions."""
        buy_price = random.randint(50, 500)
        
        if difficulty == "easy":
            sell_price = buy_price + random.randint(10, 100)
            commission_pct = random.choice([1, 2, 5])
            
            gross_profit = sell_price - buy_price
            commission = sell_price * commission_pct / 100
            net_profit = gross_profit - commission
            
            question_text = f"Buy at ${buy_price}, sell at ${sell_price}, commission is {commission_pct}%. What is your net profit?"
        elif difficulty == "medium":
            sell_price = random.randint(50, 600)
            commission_pct = random.uniform(1.5, 3.5)
            
            gross_profit = sell_price - buy_price
            commission = sell_price * commission_pct / 100
            net_profit = gross_profit - commission
            
            question_text = f"Buy at ${buy_price}, sell at ${sell_price}, commission is {commission_pct:.1f}%. What is your net profit?"
        else:  # hard
            sell_price = random.randint(50, 600)
            buy_commission_pct = random.uniform(1, 2)
            sell_commission_pct = random.uniform(1.5, 3)
            
            buy_commission = buy_price * buy_commission_pct / 100
            sell_commission = sell_price * sell_commission_pct / 100
            net_profit = sell_price - buy_price - buy_commission - sell_commission
            
            question_text = f"Buy at ${buy_price} ({buy_commission_pct:.1f}% commission), sell at ${sell_price} ({sell_commission_pct:.1f}% commission). Net profit?"
        
        answer = round(net_profit, 2)
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=str(round(answer, 2)),
            acceptable_answers=[str(round(answer, 2)), str(round(answer, 1)), str(int(answer))],
            metadata={"buy_price": buy_price, "type": "profit_calculation"}
        )
