import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


from labs.lab1.task1 import main as run_task1
from labs.lab1.task2 import main as run_task2
from labs.lab1.task3 import main as run_task3


def main():
    print("=== Task 1 ===")
    run_task1()
    print("\n=== Task 2 ===")
    run_task2()
    print("\n=== Task 3 ===")
    run_task3()


if __name__ == "__main__":
    main()
