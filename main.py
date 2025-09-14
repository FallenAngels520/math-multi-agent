"""
Main entry point for the multi-agent math problem solving system.
"""

import asyncio
from src.agents import math_solver_graph
from src.state.state_utils import initialize_state


async def main():
    """Run the math problem solving system."""
    print("=== Multi-Agent Math Problem Solver ===\n")
    
    # Test with a simple math problem
    math_problem = "Solve for x: 2x + 3 = 7"
    print(f"Problem: {math_problem}")
    
    # Initialize the state
    initial_state = initialize_state(math_problem)
    
    # Run the graph
    print("\nStarting problem solving process...")
    
    try:
        result = await math_solver_graph.ainvoke(initial_state)
        
        print("\n=== Final Result ===")
        print(f"Final Answer: {result.get('final_answer', 'No answer found')}")
        print(f"Execution Status: {result.get('execution_status', 'Unknown')}")
        print(f"Total Iterations: {result.get('total_iterations', 0)}")
        
        # Print solution steps
        if result.get('solution_steps'):
            print("\nSolution Steps:")
            for i, step in enumerate(result['solution_steps'], 1):
                print(f"{i}. {step}")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        print("Please check your setup and dependencies.")


if __name__ == "__main__":
    asyncio.run(main())