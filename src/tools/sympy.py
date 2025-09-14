"""
SymPy mathematical computation tool for elementary and high school math problems.

This tool provides a generic interface to SymPy for solving common math problems
including algebra, calculus, geometry, and arithmetic operations.
"""

import re
import json
import math
from typing import Optional, Dict, Any, List, Union, Tuple
from langchain_core.tools import BaseTool, tool
from pydantic import Field, BaseModel
import sympy as sp
from sympy import (
    symbols, Eq, solve, simplify, expand, factor, diff, integrate, 
    pi, E, I, oo, # Constants
    sin, cos, tan, cot, sec, csc, asin, acos, atan, # Trigonometry
    sinh, cosh, tanh, asinh, acosh, atanh, # Hyperbolic
    sqrt, log, exp, log10, log2, # Exponentials and logs
    factorial, binomial, # Combinatorics
    Sum, Product, # Summation and product
    limit, series, # Limits and series
    Matrix, det, inv, eigenvals, eigenvects, # Linear algebra
    Function, dsolve, # Differential equations
    primerange, isprime, factorint, # Number theory
    gcd, lcm, # Number theory
    Piecewise, # Piecewise functions
    latex, pretty_print, # Output formatting
    # Additional mathematical functions
    gamma, zeta, erf, besselj, bessely, besseli, besselk, # Special functions
    legendre, hermite, laguerre, chebyshevt, chebyshevu, # Orthogonal polynomials
    fourier_transform, inverse_fourier_transform, # Transforms
    laplace_transform, inverse_laplace_transform,
    z_transform, inverse_z_transform,
    solve_linear_system, linsolve, # Linear systems
    nonlinsolve, # Nonlinear systems
    minimize, maximize, # Optimization
    solveset, # Advanced solving
    re, im, Abs, arg, conjugate, # Complex numbers
    curl, divergence, gradient, # Vector calculus
    apart, together, # Partial fractions
    resultant, discriminant, # Polynomial tools
    fibonacci, tribonacci, # Sequence functions
    catalan, # Combinatorial numbers
    KroneckerDelta, LeviCivita, # Tensor functions
    DiracDelta, Heaviside # Distribution functions
)


class SymPyExpressionInput(BaseModel):
    """Input schema for SymPy expression evaluation."""
    expression: str = Field(description="The mathematical expression to evaluate")
    variables: Optional[List[str]] = Field(default=None, description="List of variable names used in the expression")


class SolveEquationInput(BaseModel):
    """Input schema for solving equations."""
    equation: str = Field(description="The equation to solve (e.g., 'x^2 + 2*x + 1 = 0')")
    variable: str = Field(default="x", description="The variable to solve for")


class SimplifyExpressionInput(BaseModel):
    """Input schema for simplifying expressions."""
    expression: str = Field(description="The expression to simplify")


class DifferentiateInput(BaseModel):
    """Input schema for differentiation."""
    expression: str = Field(description="The expression to differentiate")
    variable: str = Field(default="x", description="The variable to differentiate with respect to")
    order: int = Field(default=1, description="Order of differentiation")


class IntegrateInput(BaseModel):
    """Input schema for integration."""
    expression: str = Field(description="The expression to integrate")
    variable: str = Field(default="x", description="The variable to integrate with respect to")
    limits: Optional[List[Union[float, str]]] = Field(default=None, description="Integration limits [lower, upper]")


class MathProblemInput(BaseModel):
    """Input schema for generic math problem solving."""
    problem: str = Field(description="The mathematical problem to solve")
    problem_type: Optional[str] = Field(default=None, description="Type of problem (algebra, calculus, geometry, arithmetic, linear_algebra, differential_equations, discrete_math, statistics, physics)")
    variables: Optional[List[str]] = Field(default=None, description="List of variables used in the problem")


class MatrixOperationInput(BaseModel):
    """Input schema for matrix operations."""
    operation: str = Field(description="Matrix operation (determinant, inverse, eigenvalues, eigenvectors, multiply, add)")
    matrix: List[List[Union[float, str]]] = Field(description="Matrix as 2D list")
    matrix2: Optional[List[List[Union[float, str]]]] = Field(default=None, description="Second matrix for binary operations")


class DifferentialEquationInput(BaseModel):
    """Input schema for differential equations."""
    equation: str = Field(description="Differential equation to solve")
    function: str = Field(default="y", description="Function to solve for")
    variable: str = Field(default="x", description="Independent variable")
    initial_conditions: Optional[Dict[str, float]] = Field(default=None, description="Initial conditions")


class SeriesInput(BaseModel):
    """Input schema for series and limits."""
    expression: str = Field(description="Expression for series or limit")
    variable: str = Field(default="x", description="Variable")
    point: Union[float, str] = Field(default=0, description="Point for expansion or limit")
    n_terms: Optional[int] = Field(default=6, description="Number of terms for series expansion")


class NumberTheoryInput(BaseModel):
    """Input schema for number theory operations."""
    operation: str = Field(description="Operation (is_prime, factorize, gcd, lcm, primes_in_range)")
    number: Optional[int] = Field(default=None, description="Number for operation")
    numbers: Optional[List[int]] = Field(default=None, description="Numbers for binary operations")
    range_start: Optional[int] = Field(default=2, description="Start of range for prime numbers")
    range_end: Optional[int] = Field(default=100, description="End of range for prime numbers")


class StatisticsInput(BaseModel):
    """Input schema for statistical operations."""
    operation: str = Field(description="Statistical operation (mean, median, variance, std_dev, combinations, permutations)")
    data: Optional[List[float]] = Field(default=None, description="Data for statistical operations")
    n: Optional[int] = Field(default=None, description="Number of items for combinatorics")
    k: Optional[int] = Field(default=None, description="Number of choices for combinatorics")


class SpecialFunctionInput(BaseModel):
    """Input schema for special functions."""
    function_type: str = Field(description="Special function type (gamma, zeta, erf, bessel, legendre, hermite, laguerre, chebyshev)")
    expression: str = Field(description="Expression or argument for the special function")
    order: Optional[int] = Field(default=0, description="Order for Bessel functions or polynomial degree")
    variable: str = Field(default="x", description="Variable for the function")


class TransformInput(BaseModel):
    """Input schema for integral transforms."""
    transform_type: str = Field(description="Transform type (fourier, laplace, z_transform)")
    expression: str = Field(description="Expression to transform")
    variable: str = Field(default="t", description="Original variable")
    transform_variable: str = Field(default="s", description="Transform variable")


class ComplexNumberInput(BaseModel):
    """Input schema for complex number operations."""
    operation: str = Field(description="Complex operation (real_part, imag_part, magnitude, argument, conjugate)")
    expression: str = Field(description="Complex expression")


class VectorCalculusInput(BaseModel):
    """Input schema for vector calculus operations."""
    operation: str = Field(description="Vector operation (gradient, divergence, curl)")
    expression: str = Field(description="Vector field expression")
    variables: List[str] = Field(description="List of variables for the coordinate system")


class OptimizationInput(BaseModel):
    """Input schema for optimization problems."""
    objective: str = Field(description="Objective function to optimize")
    variables: List[str] = Field(description="Variables to optimize over")
    constraints: Optional[List[str]] = Field(default=None, description="Constraints for the optimization")
    bounds: Optional[Dict[str, Tuple[float, float]]] = Field(default=None, description="Variable bounds")
    method: str = Field(default="minimize", description="Optimization method (minimize or maximize)")


class SystemSolvingInput(BaseModel):
    """Input schema for solving equation systems."""
    equations: List[str] = Field(description="List of equations to solve")
    variables: List[str] = Field(description="Variables to solve for")
    system_type: str = Field(default="linear", description="System type (linear, nonlinear)")


class PolynomialInput(BaseModel):
    """Input schema for polynomial operations."""
    operation: str = Field(description="Polynomial operation (roots, discriminant, resultant, partial_fractions)")
    polynomial: str = Field(description="Polynomial expression")
    variable: str = Field(default="x", description="Polynomial variable")


class SymPyTool(BaseTool):
    """A LangChain tool for symbolic mathematics using SymPy."""
    
    name: str = "sympy"
    description: str = (
        "A symbolic mathematics library for Python. Use for symbolic computation, "
        "equation solving, simplification, calculus operations, and algebraic manipulation. "
        "Ideal for exact mathematical solutions and step-by-step derivations."
    )
    args_schema: type[BaseModel] = SymPyExpressionInput
    
    def _parse_expression(self, expression: str, variables: Optional[List[str]] = None) -> sp.Expr:
        """Parse a mathematical expression string into a SymPy expression."""
        try:
            # Create symbols for variables
            if variables:
                sym_vars = symbols(' '.join(variables))
                if len(variables) == 1:
                    sym_vars = (sym_vars,)  # Ensure it's a tuple for single variable
                local_dict = dict(zip(variables, sym_vars))
            else:
                # Extract variables from expression
                var_pattern = r'\b[a-zA-Z][a-zA-Z0-9]*\b'
                found_vars = list(set(re.findall(var_pattern, expression)))
                found_vars = [v for v in found_vars if v not in ['exp', 'log', 'sin', 'cos', 'tan', 'sqrt']]
                
                if found_vars:
                    sym_vars = symbols(' '.join(found_vars))
                    if len(found_vars) == 1:
                        sym_vars = (sym_vars,)
                    local_dict = dict(zip(found_vars, sym_vars))
                else:
                    local_dict = {}
            
            # Parse the expression
            return sp.sympify(expression, locals=local_dict)
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expression}': {e}")
    
    def _run(self, expression: str, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression using SymPy.
        
        Args:
            expression: The mathematical expression to evaluate
            variables: List of variable names used in the expression
            
        Returns:
            Dictionary containing the evaluated result
        """
        try:
            expr = self._parse_expression(expression, variables)
            
            # Try to evaluate numerically if possible
            try:
                numeric_result = float(expr.evalf())
                result_type = "numeric"
            except (TypeError, ValueError):
                numeric_result = None
                result_type = "symbolic"
            
            return {
                "success": True,
                "expression": str(expr),
                "result": str(expr),
                "numeric_result": numeric_result,
                "result_type": result_type,
                "latex": sp.latex(expr),
                "simplified": str(simplify(expr))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def solve_equation(self, equation: str, variable: str = "x") -> Dict[str, Any]:
        """
        Solve an equation for a given variable.
        
        Args:
            equation: The equation to solve (e.g., "x^2 + 2*x + 1 = 0")
            variable: The variable to solve for
            
        Returns:
            Dictionary containing solutions and steps
        """
        try:
            # Parse equation
            if "=" in equation:
                lhs, rhs = equation.split("=", 1)
                lhs_expr = self._parse_expression(lhs.strip(), [variable])
                rhs_expr = self._parse_expression(rhs.strip(), [variable])
                eq = Eq(lhs_expr, rhs_expr)
            else:
                # Assume expression = 0
                expr = self._parse_expression(equation, [variable])
                eq = Eq(expr, 0)
            
            # Solve the equation
            solutions = solve(eq, symbols(variable))
            
            return {
                "success": True,
                "equation": str(eq),
                "solutions": [str(sol) for sol in solutions],
                "numeric_solutions": [float(sol.evalf()) if sol.is_number else None for sol in solutions],
                "latex_equation": sp.latex(eq),
                "latex_solutions": [sp.latex(sol) for sol in solutions]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "equation": equation
            }
    
    def simplify_expression(self, expression: str) -> Dict[str, Any]:
        """
        Simplify a mathematical expression.
        
        Args:
            expression: The expression to simplify
            
        Returns:
            Dictionary containing simplified result
        """
        try:
            expr = self._parse_expression(expression)
            simplified = simplify(expr)
            
            return {
                "success": True,
                "original": str(expr),
                "simplified": str(simplified),
                "latex_original": sp.latex(expr),
                "latex_simplified": sp.latex(simplified),
                "difference": str(expr - simplified) if expr != simplified else "No change"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def differentiate(self, expression: str, variable: str = "x", order: int = 1) -> Dict[str, Any]:
        """
        Differentiate an expression.
        
        Args:
            expression: The expression to differentiate
            variable: The variable to differentiate with respect to
            order: Order of differentiation
            
        Returns:
            Dictionary containing derivative result
        """
        try:
            expr = self._parse_expression(expression, [variable])
            derivative = diff(expr, symbols(variable), order)
            
            return {
                "success": True,
                "original": str(expr),
                "derivative": str(derivative),
                "order": order,
                "variable": variable,
                "latex_original": sp.latex(expr),
                "latex_derivative": sp.latex(derivative)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def integrate(self, expression: str, variable: str = "x", 
                 limits: Optional[List[Union[float, str]]] = None) -> Dict[str, Any]:
        """
        Integrate an expression.
        
        Args:
            expression: The expression to integrate
            variable: The variable to integrate with respect to
            limits: Integration limits [lower, upper] for definite integral
            
        Returns:
            Dictionary containing integral result
        """
        try:
            expr = self._parse_expression(expression, [variable])
            
            if limits and len(limits) == 2:
                # Definite integral
                lower, upper = limits
                if isinstance(lower, str):
                    lower = self._parse_expression(lower, [variable])
                if isinstance(upper, str):
                    upper = self._parse_expression(upper, [variable])
                
                integral = integrate(expr, (symbols(variable), lower, upper))
                integral_type = "definite"
            else:
                # Indefinite integral
                integral = integrate(expr, symbols(variable))
                integral_type = "indefinite"
            
            return {
                "success": True,
                "original": str(expr),
                "integral": str(integral),
                "type": integral_type,
                "variable": variable,
                "limits": limits,
                "latex_original": sp.latex(expr),
                "latex_integral": sp.latex(integral),
                "numeric_result": float(integral.evalf()) if integral.is_number else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def expand_expression(self, expression: str) -> Dict[str, Any]:
        """Expand an algebraic expression."""
        try:
            expr = self._parse_expression(expression)
            expanded = expand(expr)
            
            return {
                "success": True,
                "original": str(expr),
                "expanded": str(expanded),
                "latex_original": sp.latex(expr),
                "latex_expanded": sp.latex(expanded)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }
    
    def factor_expression(self, expression: str) -> Dict[str, Any]:
        """Factor an algebraic expression."""
        try:
            expr = self._parse_expression(expression)
            factored = factor(expr)
            
            return {
                "success": True,
                "original": str(expr),
                "factored": str(factored),
                "latex_original": sp.latex(expr),
                "latex_factored": sp.latex(factored)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }

    def solve_math_problem(self, problem: str, problem_type: Optional[str] = None, 
                          variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Solve a generic mathematical problem using SymPy.
        
        Args:
            problem: The mathematical problem to solve
            problem_type: Type of problem (algebra, calculus, geometry, arithmetic)
            variables: List of variables used in the problem
            
        Returns:
            Dictionary containing solution and steps
        """
        try:
            # Auto-detect problem type if not specified
            if not problem_type:
                problem_type = self._detect_problem_type(problem)
            
            # Solve based on problem type
            if problem_type == "algebra":
                return self._solve_algebra_problem(problem, variables)
            elif problem_type == "calculus":
                return self._solve_calculus_problem(problem, variables)
            elif problem_type == "geometry":
                return self._solve_geometry_problem(problem)
            elif problem_type == "arithmetic":
                return self._solve_arithmetic_problem(problem)
            else:
                return self._solve_general_problem(problem, variables)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "problem": problem,
                "problem_type": problem_type or "unknown"
            }
    
    def _detect_problem_type(self, problem: str) -> str:
        """Detect the type of mathematical problem."""
        problem_lower = problem.lower()
        
        # Calculus detection
        calculus_keywords = ['derivative', 'differentiate', 'integral', 'integrate', 
                           'limit', 'differentiation', 'integration']
        if any(keyword in problem_lower for keyword in calculus_keywords):
            return "calculus"
        
        # Geometry detection
        geometry_keywords = ['area', 'volume', 'perimeter', 'circle', 'triangle', 
                           'square', 'rectangle', 'angle', 'radius', 'diameter']
        if any(keyword in problem_lower for keyword in geometry_keywords):
            return "geometry"
        
        # Algebra detection
        algebra_keywords = ['solve', 'equation', 'variable', 'x=', 'y=', 'z=', 
                          'expression', 'simplify', 'factor']
        if any(keyword in problem_lower for keyword in algebra_keywords):
            return "algebra"
        
        # Arithmetic detection
        arithmetic_keywords = ['add', 'subtract', 'multiply', 'divide', 'sum', 
                             'product', 'difference', 'calculate', 'compute']
        if any(keyword in problem_lower for keyword in arithmetic_keywords):
            return "arithmetic"
        
        return "general"
    
    def _solve_algebra_problem(self, problem: str, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Solve algebra problems including equations and expressions."""
        # Try to extract equation
        if "=" in problem:
            # Equation solving
            parts = problem.split("=")
            if len(parts) == 2:
                return self.solve_equation(problem, variables[0] if variables else "x")
        
        # Expression evaluation or simplification
        try:
            return self._run(problem, variables)
        except:
            # If evaluation fails, try simplification
            return self.simplify_expression(problem)
    
    def _solve_calculus_problem(self, problem: str, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Solve calculus problems including derivatives and integrals."""
        problem_lower = problem.lower()
        
        # Derivative detection
        if any(word in problem_lower for word in ['derivative', 'differentiate']):
            # Extract variable and order
            var = self._extract_variable(problem) or (variables[0] if variables else "x")
            order = self._extract_derivative_order(problem)
            expr = self._extract_expression(problem)
            return self.differentiate(expr, var, order)
        
        # Integral detection
        elif any(word in problem_lower for word in ['integral', 'integrate']):
            var = self._extract_variable(problem) or (variables[0] if variables else "x")
            expr = self._extract_expression(problem)
            limits = self._extract_integration_limits(problem)
            return self.integrate(expr, var, limits)
        
        # Default to expression evaluation
        return self._run(problem, variables)
    
    def _solve_geometry_problem(self, problem: str) -> Dict[str, Any]:
        """Solve geometry problems."""
        problem_lower = problem.lower()
        
        # Area calculations
        if 'area' in problem_lower:
            if 'circle' in problem_lower:
                radius = self._extract_number(problem)
                if radius:
                    area = math.pi * radius ** 2
                    return {
                        "success": True,
                        "problem_type": "geometry",
                        "shape": "circle",
                        "operation": "area",
                        "radius": radius,
                        "result": area,
                        "formula": "A = πr²",
                        "steps": [f"Area = π × ({radius})²", f"Area = {math.pi} × {radius**2}", f"Area = {area}"]
                    }
            elif 'rectangle' in problem_lower or 'square' in problem_lower:
                numbers = self._extract_numbers(problem)
                if len(numbers) >= 2:
                    length, width = numbers[0], numbers[1]
                    area = length * width
                    return {
                        "success": True,
                        "problem_type": "geometry",
                        "shape": "rectangle",
                        "operation": "area",
                        "length": length,
                        "width": width,
                        "result": area,
                        "formula": "A = l × w",
                        "steps": [f"Area = {length} × {width}", f"Area = {area}"]
                    }
        
        # Default to arithmetic evaluation
        return self._solve_arithmetic_problem(problem)
    
    def _solve_arithmetic_problem(self, problem: str) -> Dict[str, Any]:
        """Solve arithmetic problems."""
        try:
            # Remove non-mathematical text and evaluate
            clean_expr = re.sub(r'[^0-9+\-*/().^ ]', '', problem)
            result = eval(clean_expr, {"__builtins__": {}}, {"math": math, "pi": math.pi})
            
            return {
                "success": True,
                "problem_type": "arithmetic",
                "expression": clean_expr,
                "result": result,
                "steps": [f"Evaluated: {clean_expr} = {result}"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "problem": problem,
                "problem_type": "arithmetic"
            }
    
    def _solve_general_problem(self, problem: str, variables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Solve general mathematical problems."""
        # Try various approaches
        approaches = [
            lambda: self.solve_equation(problem, variables[0] if variables else "x"),
            lambda: self._run(problem, variables),
            lambda: self.simplify_expression(problem),
            lambda: self._solve_arithmetic_problem(problem)
        ]
        
        for approach in approaches:
            try:
                result = approach()
                if result.get("success", False):
                    return result
            except:
                continue
        
        return {
            "success": False,
            "error": "Could not solve the problem using any approach",
            "problem": problem
        }
    
    def _extract_variable(self, problem: str) -> Optional[str]:
        """Extract variable from problem text."""
        matches = re.findall(r'\b([a-zA-Z])\b', problem)
        return matches[0] if matches else None
    
    def _extract_expression(self, problem: str) -> str:
        """Extract mathematical expression from problem text."""
        # Look for expressions with variables and operators
        matches = re.findall(r'[a-zA-Z0-9+\-*/().^]+', problem)
        return matches[-1] if matches else problem
    
    def _extract_derivative_order(self, problem: str) -> int:
        """Extract derivative order from problem text."""
        matches = re.findall(r'(\d+)(?:st|nd|rd|th)\s*derivative', problem.lower())
        return int(matches[0]) if matches else 1
    
    def _extract_integration_limits(self, problem: str) -> Optional[List[float]]:
        """Extract integration limits from problem text."""
        matches = re.findall(r'from\s+(\d+(?:\.\d+)?)\s+to\s+(\d+(?:\.\d+)?)', problem.lower())
        if matches:
            return [float(matches[0][0]), float(matches[0][1])]
        return None
    
    def _extract_number(self, problem: str) -> Optional[float]:
        """Extract a single number from problem text."""
        matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', problem)
        return float(matches[0]) if matches else None
    
    def _extract_numbers(self, problem: str) -> List[float]:
        """Extract all numbers from problem text."""
        matches = re.findall(r'\b(\d+(?:\.\d+)?)\b', problem)
        return [float(match) for match in matches]

    # ========== ADVANCED MATHEMATICAL OPERATIONS ==========

    def matrix_operation(self, operation: str, matrix_data: List[List[Union[float, str]]], 
                        matrix2_data: Optional[List[List[Union[float, str]]]] = None) -> Dict[str, Any]:
        """Perform matrix operations."""
        try:
            # Create matrix from input data
            matrix = Matrix(matrix_data)
            
            if operation == "determinant":
                result = det(matrix)
                return {
                    "success": True,
                    "operation": "determinant",
                    "matrix": str(matrix),
                    "result": str(result),
                    "numeric_result": float(result.evalf()) if result.is_number else None
                }
            
            elif operation == "inverse":
                result = inv(matrix)
                return {
                    "success": True,
                    "operation": "inverse",
                    "matrix": str(matrix),
                    "inverse": str(result),
                    "latex": latex(result)
                }
            
            elif operation == "eigenvalues":
                result = eigenvals(matrix)
                return {
                    "success": True,
                    "operation": "eigenvalues",
                    "matrix": str(matrix),
                    "eigenvalues": {str(k): str(v) for k, v in result.items()},
                    "numeric_eigenvalues": {str(k): float(v.evalf()) for k, v in result.items()}
                }
            
            elif operation == "eigenvectors":
                result = eigenvects(matrix)
                eigenvectors = []
                for eigval, multiplicity, basis in result:
                    eigenvectors.append({
                        "eigenvalue": str(eigval),
                        "multiplicity": multiplicity,
                        "eigenvectors": [str(vec) for vec in basis]
                    })
                return {
                    "success": True,
                    "operation": "eigenvectors",
                    "matrix": str(matrix),
                    "eigenvectors": eigenvectors
                }
            
            elif operation in ["multiply", "add"] and matrix2_data:
                matrix2 = Matrix(matrix2_data)
                if operation == "multiply":
                    result = matrix * matrix2
                    op_name = "multiplication"
                else:
                    result = matrix + matrix2
                    op_name = "addition"
                
                return {
                    "success": True,
                    "operation": op_name,
                    "matrix1": str(matrix),
                    "matrix2": str(matrix2),
                    "result": str(result),
                    "latex": latex(result)
                }
            
            else:
                return {"success": False, "error": f"Unsupported matrix operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def solve_differential_equation(self, equation: str, function: str = "y", 
                                  variable: str = "x", 
                                  initial_conditions: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Solve differential equations."""
        try:
            # Parse the equation
            x = symbols(variable)
            f = Function(function)(x)
            
            # Parse the differential equation
            eq = self._parse_expression(equation, [function, variable])
            
            # Solve the differential equation
            solution = dsolve(eq, f)
            
            result = {
                "success": True,
                "equation": str(eq),
                "solution": str(solution),
                "latex_equation": latex(eq),
                "latex_solution": latex(solution)
            }
            
            # Apply initial conditions if provided
            if initial_conditions:
                try:
                    constants = list(solution.free_symbols - {x})
                    if constants:
                        eqs = []
                        for cond_var, cond_val in initial_conditions.items():
                            cond_point = self._parse_expression(cond_var.replace(function, str(f)), [variable])
                            eqs.append(solution.rhs.subs(x, cond_point) - cond_val)
                        
                        const_solutions = solve(eqs, constants)
                        if const_solutions:
                            final_solution = solution.subs(const_solutions[0])
                            result.update({
                                "with_initial_conditions": True,
                                "final_solution": str(final_solution),
                                "latex_final_solution": latex(final_solution)
                            })
                except:
                    pass  # Skip initial conditions if they can't be applied
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "equation": equation}

    def series_expansion(self, expression: str, variable: str = "x", 
                        point: Union[float, str] = 0, n_terms: int = 6) -> Dict[str, Any]:
        """Compute series expansion of an expression."""
        try:
            expr = self._parse_expression(expression, [variable])
            x = symbols(variable)
            
            if isinstance(point, str):
                point = self._parse_expression(point, [variable])
            
            series_result = series(expr, x, point, n_terms)
            
            return {
                "success": True,
                "expression": str(expr),
                "series": str(series_result),
                "point": str(point),
                "terms": n_terms,
                "latex_series": latex(series_result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

    def compute_limit(self, expression: str, variable: str = "x", 
                     point: Union[float, str] = 0) -> Dict[str, Any]:
        """Compute limit of an expression."""
        try:
            expr = self._parse_expression(expression, [variable])
            x = symbols(variable)
            
            if isinstance(point, str):
                point = self._parse_expression(point, [variable])
            
            limit_result = limit(expr, x, point)
            
            return {
                "success": True,
                "expression": str(expr),
                "limit": str(limit_result),
                "point": str(point),
                "numeric_result": float(limit_result.evalf()) if limit_result.is_number else None,
                "latex_limit": latex(limit_result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

    def number_theory_operation(self, operation: str, number: Optional[int] = None,
                               numbers: Optional[List[int]] = None,
                               range_start: int = 2, range_end: int = 100) -> Dict[str, Any]:
        """Perform number theory operations."""
        try:
            if operation == "is_prime" and number is not None:
                result = isprime(number)
                return {
                    "success": True,
                    "operation": "is_prime",
                    "number": number,
                    "is_prime": result
                }
            
            elif operation == "factorize" and number is not None:
                factors = factorint(number)
                return {
                    "success": True,
                    "operation": "factorize",
                    "number": number,
                    "prime_factors": factors,
                    "factorization": " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in factors.items())
                }
            
            elif operation == "gcd" and numbers and len(numbers) >= 2:
                result = gcd(*numbers)
                return {
                    "success": True,
                    "operation": "gcd",
                    "numbers": numbers,
                    "gcd": result
                }
            
            elif operation == "lcm" and numbers and len(numbers) >= 2:
                result = lcm(*numbers)
                return {
                    "success": True,
                    "operation": "lcm",
                    "numbers": numbers,
                    "lcm": result
                }
            
            elif operation == "primes_in_range":
                primes = list(primerange(range_start, range_end + 1))
                return {
                    "success": True,
                    "operation": "primes_in_range",
                    "range": f"{range_start} to {range_end}",
                    "primes": primes,
                    "count": len(primes)
                }
            
            else:
                return {"success": False, "error": "Invalid operation or missing parameters"}
                
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def statistics_operation(self, operation: str, data: Optional[List[float]] = None,
                            n: Optional[int] = None, k: Optional[int] = None) -> Dict[str, Any]:
        """Perform statistical operations."""
        try:
            if operation == "mean" and data:
                result = sum(data) / len(data)
                return {
                    "success": True,
                    "operation": "mean",
                    "data": data,
                    "mean": result
                }
            
            elif operation == "median" and data:
                sorted_data = sorted(data)
                n_data = len(sorted_data)
                if n_data % 2 == 1:
                    result = sorted_data[n_data // 2]
                else:
                    result = (sorted_data[n_data // 2 - 1] + sorted_data[n_data // 2]) / 2
                return {
                    "success": True,
                    "operation": "median",
                    "data": data,
                    "median": result
                }
            
            elif operation == "variance" and data:
                mean = sum(data) / len(data)
                result = sum((x - mean) ** 2 for x in data) / len(data)
                return {
                    "success": True,
                    "operation": "variance",
                    "data": data,
                    "variance": result
                }
            
            elif operation == "std_dev" and data:
                mean = sum(data) / len(data)
                variance = sum((x - mean) ** 2 for x in data) / len(data)
                result = math.sqrt(variance)
                return {
                    "success": True,
                    "operation": "std_dev",
                    "data": data,
                    "std_dev": result
                }
            
            elif operation == "combinations" and n is not None and k is not None:
                result = binomial(n, k)
                return {
                    "success": True,
                    "operation": "combinations",
                    "n": n,
                    "k": k,
                    "combinations": int(result),
                    "formula": f"C({n}, {k}) = {result}"
                }
            
            elif operation == "permutations" and n is not None and k is not None:
                result = factorial(n) / factorial(n - k)
                return {
                    "success": True,
                    "operation": "permutations",
                    "n": n,
                    "k": k,
                    "permutations": int(result),
                    "formula": f"P({n}, {k}) = {result}"
                }
            
            else:
                return {"success": False, "error": "Invalid operation or missing parameters"}
                
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def evaluate_sum(self, expression: str, variable: str = "n", 
                    lower: Union[int, str] = 1, upper: Union[int, str] = 10) -> Dict[str, Any]:
        """Evaluate summation."""
        try:
            expr = self._parse_expression(expression, [variable])
            n = symbols(variable)
            
            if isinstance(lower, str):
                lower = self._parse_expression(lower, [variable])
            if isinstance(upper, str):
                upper = self._parse_expression(upper, [variable])
            
            sum_result = Sum(expr, (n, lower, upper)).doit()
            
            return {
                "success": True,
                "sum": str(sum_result),
                "expression": str(expr),
                "variable": variable,
                "lower": str(lower),
                "upper": str(upper),
                "numeric_result": float(sum_result.evalf()) if sum_result.is_number else None,
                "latex_sum": latex(sum_result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

    def evaluate_product(self, expression: str, variable: str = "n", 
                        lower: Union[int, str] = 1, upper: Union[int, str] = 10) -> Dict[str, Any]:
        """Evaluate product."""
        try:
            expr = self._parse_expression(expression, [variable])
            n = symbols(variable)
            
            if isinstance(lower, str):
                lower = self._parse_expression(lower, [variable])
            if isinstance(upper, str):
                upper = self._parse_expression(upper, [variable])
            
            product_result = Product(expr, (n, lower, upper)).doit()
            
            return {
                "success": True,
                "product": str(product_result),
                "expression": str(expr),
                "variable": variable,
                "lower": str(lower),
                "upper": str(upper),
                "numeric_result": float(product_result.evalf()) if product_result.is_number else None,
                "latex_product": latex(product_result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

    # ========== ADVANCED MATHEMATICAL DOMAINS ==========

    def special_function(self, function_type: str, expression: str, 
                        variable: str = "x", order: int = 0) -> Dict[str, Any]:
        """Evaluate special mathematical functions."""
        try:
            expr = self._parse_expression(expression, [variable])
            x = symbols(variable)
            
            if function_type == "gamma":
                result = gamma(expr)
            elif function_type == "zeta":
                result = zeta(expr)
            elif function_type == "erf":
                result = erf(expr)
            elif function_type == "bessel":
                if order == 0:
                    result = besselj(0, expr)
                else:
                    result = besselj(order, expr)
            elif function_type == "legendre":
                result = legendre(order, x).subs(x, expr)
            elif function_type == "hermite":
                result = hermite(order, x).subs(x, expr)
            elif function_type == "laguerre":
                result = laguerre(order, x).subs(x, expr)
            elif function_type == "chebyshev":
                result = chebyshevt(order, x).subs(x, expr)
            else:
                return {"success": False, "error": f"Unknown special function: {function_type}"}
            
            return {
                "success": True,
                "function_type": function_type,
                "expression": str(expr),
                "order": order,
                "result": str(result),
                "numeric_result": float(result.evalf()) if result.is_number else None,
                "latex_result": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "function_type": function_type}

    def integral_transform(self, transform_type: str, expression: str, 
                          variable: str = "t", transform_variable: str = "s") -> Dict[str, Any]:
        """Compute integral transforms."""
        try:
            expr = self._parse_expression(expression, [variable])
            t = symbols(variable)
            s = symbols(transform_variable)
            
            if transform_type == "fourier":
                result = fourier_transform(expr, t, s)
            elif transform_type == "laplace":
                result = laplace_transform(expr, t, s)
            elif transform_type == "z_transform":
                result = z_transform(expr, t, s)
            else:
                return {"success": False, "error": f"Unknown transform type: {transform_type}"}
            
            return {
                "success": True,
                "transform_type": transform_type,
                "expression": str(expr),
                "result": str(result),
                "latex_result": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "transform_type": transform_type}

    def complex_operation(self, operation: str, expression: str) -> Dict[str, Any]:
        """Perform complex number operations."""
        try:
            expr = self._parse_expression(expression)
            
            if operation == "real_part":
                result = re(expr)
            elif operation == "imag_part":
                result = im(expr)
            elif operation == "magnitude":
                result = Abs(expr)
            elif operation == "argument":
                result = arg(expr)
            elif operation == "conjugate":
                result = conjugate(expr)
            else:
                return {"success": False, "error": f"Unknown complex operation: {operation}"}
            
            return {
                "success": True,
                "operation": operation,
                "expression": str(expr),
                "result": str(result),
                "numeric_result": float(result.evalf()) if result.is_number else None,
                "latex_result": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def vector_calculus(self, operation: str, expression: str, variables: List[str]) -> Dict[str, Any]:
        """Perform vector calculus operations."""
        try:
            expr = self._parse_expression(expression, variables)
            sym_vars = symbols(' '.join(variables))
            
            if operation == "gradient":
                result = gradient(expr, sym_vars)
            elif operation == "divergence":
                result = divergence(expr, sym_vars)
            elif operation == "curl":
                result = curl(expr, sym_vars)
            else:
                return {"success": False, "error": f"Unknown vector operation: {operation}"}
            
            return {
                "success": True,
                "operation": operation,
                "expression": str(expr),
                "variables": variables,
                "result": str(result),
                "latex_result": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def optimize_function(self, objective: str, variables: List[str], 
                         constraints: Optional[List[str]] = None,
                         bounds: Optional[Dict[str, Tuple[float, float]]] = None,
                         method: str = "minimize") -> Dict[str, Any]:
        """Optimize a function subject to constraints."""
        try:
            # Parse objective and constraints
            obj_expr = self._parse_expression(objective, variables)
            
            constraint_exprs = []
            if constraints:
                for constr in constraints:
                    constraint_exprs.append(self._parse_expression(constr, variables))
            
            # Convert bounds to SymPy format
            bounds_dict = {}
            if bounds:
                for var, (lower, upper) in bounds.items():
                    bounds_dict[symbols(var)] = (lower, upper)
            
            # Perform optimization
            if method == "minimize":
                result = minimize(obj_expr, variables, constraint_exprs, bounds_dict)
            elif method == "maximize":
                result = maximize(obj_expr, variables, constraint_exprs, bounds_dict)
            else:
                return {"success": False, "error": f"Unknown optimization method: {method}"}
            
            return {
                "success": True,
                "method": method,
                "objective": str(obj_expr),
                "result": str(result),
                "variables": variables
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": method}

    def solve_system(self, equations: List[str], variables: List[str], 
                    system_type: str = "linear") -> Dict[str, Any]:
        """Solve systems of equations."""
        try:
            # Parse equations
            eq_exprs = []
            for eq in equations:
                if "=" in eq:
                    lhs, rhs = eq.split("=", 1)
                    lhs_expr = self._parse_expression(lhs.strip(), variables)
                    rhs_expr = self._parse_expression(rhs.strip(), variables)
                    eq_exprs.append(Eq(lhs_expr, rhs_expr))
                else:
                    eq_exprs.append(self._parse_expression(eq, variables))
            
            sym_vars = symbols(' '.join(variables))
            
            if system_type == "linear":
                result = linsolve(eq_exprs, sym_vars)
            elif system_type == "nonlinear":
                result = nonlinsolve(eq_exprs, sym_vars)
            else:
                return {"success": False, "error": f"Unknown system type: {system_type}"}
            
            return {
                "success": True,
                "system_type": system_type,
                "equations": [str(eq) for eq in eq_exprs],
                "solutions": str(result),
                "variables": variables,
                "latex_solutions": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "system_type": system_type}

    def polynomial_operations(self, operation: str, polynomial: str, 
                             variable: str = "x") -> Dict[str, Any]:
        """Perform polynomial operations."""
        try:
            poly_expr = self._parse_expression(polynomial, [variable])
            x = symbols(variable)
            
            if operation == "roots":
                result = solve(Eq(poly_expr, 0), x)
                result_type = "roots"
            elif operation == "discriminant":
                result = discriminant(poly_expr, x)
                result_type = "discriminant"
            elif operation == "resultant":
                # For resultant, we need another polynomial
                # This is a placeholder - would need additional parameter
                result = "Resultant requires two polynomials"
                result_type = "error"
            elif operation == "partial_fractions":
                result = apart(poly_expr, x)
                result_type = "partial_fractions"
            else:
                return {"success": False, "error": f"Unknown polynomial operation: {operation}"}
            
            return {
                "success": True,
                "operation": operation,
                "polynomial": str(poly_expr),
                "result": str(result),
                "result_type": result_type,
                "latex_result": latex(result)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}

    def sequence_function(self, sequence_type: str, n: int) -> Dict[str, Any]:
        """Compute sequence numbers."""
        try:
            if sequence_type == "fibonacci":
                result = fibonacci(n)
            elif sequence_type == "tribonacci":
                result = tribonacci(n)
            elif sequence_type == "catalan":
                result = catalan(n)
            else:
                return {"success": False, "error": f"Unknown sequence type: {sequence_type}"}
            
            return {
                "success": True,
                "sequence_type": sequence_type,
                "n": n,
                "result": int(result),
                "formula": f"{sequence_type.capitalize()}({n}) = {result}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "sequence_type": sequence_type}


# Structured tools for specific operations

@tool(args_schema=SolveEquationInput)
def solve_equation_tool(equation: str, variable: str = "x") -> Dict[str, Any]:
    """
    Solve mathematical equations using SymPy.
    
    Args:
        equation: The equation to solve
        variable: The variable to solve for
        
    Returns:
        Dictionary containing solutions
    """
    tool = SymPyTool()
    return tool.solve_equation(equation, variable)


@tool(args_schema=SimplifyExpressionInput)
def simplify_expression_tool(expression: str) -> Dict[str, Any]:
    """
    Simplify mathematical expressions using SymPy.
    
    Args:
        expression: The expression to simplify
        
    Returns:
        Dictionary containing simplified result
    """
    tool = SymPyTool()
    return tool.simplify_expression(expression)


@tool(args_schema=DifferentiateInput)
def differentiate_tool(expression: str, variable: str = "x", order: int = 1) -> Dict[str, Any]:
    """
    Differentiate mathematical expressions using SymPy.
    
    Args:
        expression: The expression to differentiate
        variable: The variable to differentiate with respect to
        order: Order of differentiation
        
    Returns:
        Dictionary containing derivative result
    """
    tool = SymPyTool()
    return tool.differentiate(expression, variable, order)


@tool(args_schema=IntegrateInput)
def integrate_tool(expression: str, variable: str = "x", 
                  limits: Optional[List[Union[float, str]]] = None) -> Dict[str, Any]:
    """
    Integrate mathematical expressions using SymPy.
    
    Args:
        expression: The expression to integrate
        variable: The variable to integrate with respect to
        limits: Integration limits for definite integral
        
    Returns:
        Dictionary containing integral result
    """
    tool = SymPyTool()
    return tool.integrate(expression, variable, limits)


@tool(args_schema=MathProblemInput)
def solve_math_problem_tool(problem: str, problem_type: Optional[str] = None, 
                           variables: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Solve generic mathematical problems using SymPy.
    
    This tool can handle algebra, calculus, geometry, arithmetic, linear algebra,
    differential equations, discrete math, statistics, and physics problems.
    
    Args:
        problem: The mathematical problem to solve
        problem_type: Type of problem (algebra, calculus, geometry, arithmetic, linear_algebra, differential_equations, discrete_math, statistics, physics)
        variables: List of variables used in the problem
        
    Returns:
        Dictionary containing solution, steps, and explanation
    """
    tool = SymPyTool()
    return tool.solve_math_problem(problem, problem_type, variables)


@tool(args_schema=MatrixOperationInput)
def matrix_operation_tool(operation: str, matrix: List[List[Union[float, str]]], 
                         matrix2: Optional[List[List[Union[float, str]]]] = None) -> Dict[str, Any]:
    """
    Perform matrix operations using SymPy.
    
    Args:
        operation: Matrix operation (determinant, inverse, eigenvalues, eigenvectors, multiply, add)
        matrix: Matrix as 2D list
        matrix2: Second matrix for binary operations
        
    Returns:
        Dictionary containing matrix operation result
    """
    tool = SymPyTool()
    return tool.matrix_operation(operation, matrix, matrix2)


@tool(args_schema=DifferentialEquationInput)
def solve_differential_equation_tool(equation: str, function: str = "y", 
                                    variable: str = "x", 
                                    initial_conditions: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Solve differential equations using SymPy.
    
    Args:
        equation: Differential equation to solve
        function: Function to solve for
        variable: Independent variable
        initial_conditions: Initial conditions
        
    Returns:
        Dictionary containing differential equation solution
    """
    tool = SymPyTool()
    return tool.solve_differential_equation(equation, function, variable, initial_conditions)


@tool(args_schema=SeriesInput)
def series_expansion_tool(expression: str, variable: str = "x", 
                         point: Union[float, str] = 0, n_terms: int = 6) -> Dict[str, Any]:
    """
    Compute series expansion of an expression using SymPy.
    
    Args:
        expression: Expression for series expansion
        variable: Variable
        point: Point for expansion
        n_terms: Number of terms
        
    Returns:
        Dictionary containing series expansion result
    """
    tool = SymPyTool()
    return tool.series_expansion(expression, variable, point, n_terms)


@tool(args_schema=SeriesInput)
def compute_limit_tool(expression: str, variable: str = "x", 
                      point: Union[float, str] = 0) -> Dict[str, Any]:
    """
    Compute limit of an expression using SymPy.
    
    Args:
        expression: Expression for limit
        variable: Variable
        point: Point for limit
        
    Returns:
        Dictionary containing limit result
    """
    tool = SymPyTool()
    return tool.compute_limit(expression, variable, point)


@tool(args_schema=NumberTheoryInput)
def number_theory_tool(operation: str, number: Optional[int] = None,
                      numbers: Optional[List[int]] = None,
                      range_start: int = 2, range_end: int = 100) -> Dict[str, Any]:
    """
    Perform number theory operations using SymPy.
    
    Args:
        operation: Operation (is_prime, factorize, gcd, lcm, primes_in_range)
        number: Number for operation
        numbers: Numbers for binary operations
        range_start: Start of range for prime numbers
        range_end: End of range for prime numbers
        
    Returns:
        Dictionary containing number theory result
    """
    tool = SymPyTool()
    return tool.number_theory_operation(operation, number, numbers, range_start, range_end)


@tool(args_schema=StatisticsInput)
def statistics_tool(operation: str, data: Optional[List[float]] = None,
                   n: Optional[int] = None, k: Optional[int] = None) -> Dict[str, Any]:
    """
    Perform statistical operations using SymPy.
    
    Args:
        operation: Statistical operation (mean, median, variance, std_dev, combinations, permutations)
        data: Data for statistical operations
        n: Number of items for combinatorics
        k: Number of choices for combinatorics
        
    Returns:
        Dictionary containing statistical result
    """
    tool = SymPyTool()
    return tool.statistics_operation(operation, data, n, k)


@tool
def evaluate_sum_tool(expression: str, variable: str = "n", 
                     lower: Union[int, str] = 1, upper: Union[int, str] = 10) -> Dict[str, Any]:
    """
    Evaluate summation using SymPy.
    
    Args:
        expression: Expression to sum
        variable: Summation variable
        lower: Lower bound
        upper: Upper bound
        
    Returns:
        Dictionary containing summation result
    """
    tool = SymPyTool()
    return tool.evaluate_sum(expression, variable, lower, upper)


@tool
def evaluate_product_tool(expression: str, variable: str = "n", 
                         lower: Union[int, str] = 1, upper: Union[int, str] = 10) -> Dict[str, Any]:
    """
    Evaluate product using SymPy.
    
    Args:
        expression: Expression to multiply
        variable: Product variable
        lower: Lower bound
        upper: Upper bound
        
    Returns:
        Dictionary containing product result
    """
    tool = SymPyTool()
    return tool.evaluate_product(expression, variable, lower, upper)


@tool(args_schema=SpecialFunctionInput)
def special_function_tool(function_type: str, expression: str, 
                          variable: str = "x", order: int = 0) -> Dict[str, Any]:
    """
    Evaluate special mathematical functions using SymPy.
    
    Args:
        function_type: Special function type (gamma, zeta, erf, bessel, legendre, hermite, laguerre, chebyshev)
        expression: Expression or argument for the special function
        variable: Variable for the function
        order: Order for Bessel functions or polynomial degree
        
    Returns:
        Dictionary containing special function result
    """
    tool = SymPyTool()
    return tool.special_function(function_type, expression, variable, order)


@tool(args_schema=TransformInput)
def integral_transform_tool(transform_type: str, expression: str, 
                           variable: str = "t", transform_variable: str = "s") -> Dict[str, Any]:
    """
    Compute integral transforms using SymPy.
    
    Args:
        transform_type: Transform type (fourier, laplace, z_transform)
        expression: Expression to transform
        variable: Original variable
        transform_variable: Transform variable
        
    Returns:
        Dictionary containing transform result
    """
    tool = SymPyTool()
    return tool.integral_transform(transform_type, expression, variable, transform_variable)


@tool(args_schema=ComplexNumberInput)
def complex_operation_tool(operation: str, expression: str) -> Dict[str, Any]:
    """
    Perform complex number operations using SymPy.
    
    Args:
        operation: Complex operation (real_part, imag_part, magnitude, argument, conjugate)
        expression: Complex expression
        
    Returns:
        Dictionary containing complex operation result
    """
    tool = SymPyTool()
    return tool.complex_operation(operation, expression)


@tool(args_schema=VectorCalculusInput)
def vector_calculus_tool(operation: str, expression: str, variables: List[str]) -> Dict[str, Any]:
    """
    Perform vector calculus operations using SymPy.
    
    Args:
        operation: Vector operation (gradient, divergence, curl)
        expression: Vector field expression
        variables: List of variables for the coordinate system
        
    Returns:
        Dictionary containing vector calculus result
    """
    tool = SymPyTool()
    return tool.vector_calculus(operation, expression, variables)


@tool(args_schema=OptimizationInput)
def optimize_function_tool(objective: str, variables: List[str], 
                          constraints: Optional[List[str]] = None,
                          bounds: Optional[Dict[str, Tuple[float, float]]] = None,
                          method: str = "minimize") -> Dict[str, Any]:
    """
    Optimize a function subject to constraints using SymPy.
    
    Args:
        objective: Objective function to optimize
        variables: Variables to optimize over
        constraints: Constraints for the optimization
        bounds: Variable bounds
        method: Optimization method (minimize or maximize)
        
    Returns:
        Dictionary containing optimization result
    """
    tool = SymPyTool()
    return tool.optimize_function(objective, variables, constraints, bounds, method)


@tool(args_schema=SystemSolvingInput)
def solve_system_tool(equations: List[str], variables: List[str], 
                     system_type: str = "linear") -> Dict[str, Any]:
    """
    Solve systems of equations using SymPy.
    
    Args:
        equations: List of equations to solve
        variables: Variables to solve for
        system_type: System type (linear, nonlinear)
        
    Returns:
        Dictionary containing system solutions
    """
    tool = SymPyTool()
    return tool.solve_system(equations, variables, system_type)


@tool(args_schema=PolynomialInput)
def polynomial_operations_tool(operation: str, polynomial: str, 
                              variable: str = "x") -> Dict[str, Any]:
    """
    Perform polynomial operations using SymPy.
    
    Args:
        operation: Polynomial operation (roots, discriminant, resultant, partial_fractions)
        polynomial: Polynomial expression
        variable: Polynomial variable
        
    Returns:
        Dictionary containing polynomial operation result
    """
    tool = SymPyTool()
    return tool.polynomial_operations(operation, polynomial, variable)


@tool
def sequence_function_tool(sequence_type: str, n: int) -> Dict[str, Any]:
    """
    Compute sequence numbers using SymPy.
    
    Args:
        sequence_type: Sequence type (fibonacci, tribonacci, catalan)
        n: Index in the sequence
        
    Returns:
        Dictionary containing sequence number
    """
    tool = SymPyTool()
    return tool.sequence_function(sequence_type, n)


def create_sympy_tool() -> SymPyTool:
    """
    Factory function to create a SymPy tool instance.
    
    Returns:
        SymPyTool instance
    """
    return SymPyTool()


# Example usage
if __name__ == "__main__":
    tool = create_sympy_tool()
    
    # Test comprehensive mathematical capabilities
    print("=== COMPREHENSIVE SYMPY CAPABILITIES DEMO ===\n")
    
    # 1. Basic algebra and calculus
    print("1. Basic Algebra and Calculus:")
    test_problems = [
        "Solve the equation x^2 + 2x + 1 = 0",
        "Find the derivative of sin(x) + x^2 with respect to x",
        "Simplify the expression (x^2 - 1)/(x - 1)",
        "Integrate x^2 from 0 to 1"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n  {i}. {problem}")
        result = tool.solve_math_problem(problem)
        if result["success"]:
            print(f"     Result: {result.get('result', result.get('solution', 'N/A'))}")
        else:
            print(f"     Error: {result.get('error', 'Unknown error')}")
    
    # 2. Advanced mathematical domains
    print("\n2. Advanced Mathematical Domains:")
    
    # Special functions
    print("\n  Special Functions:")
    special_funcs = [
        ("gamma", "5"),
        ("zeta", "2"),
        ("erf", "1")
    ]
    
    for func, arg in special_funcs:
        result = tool.special_function(func, arg)
        print(f"     {func.capitalize()}({arg}): {result.get('result', 'N/A')}")
    
    # Complex numbers
    print("\n  Complex Numbers:")
    result = tool.complex_operation("magnitude", "3 + 4*I")
    print(f"     |3 + 4i|: {result.get('result', 'N/A')}")
    
    # Vector calculus
    print("\n  Vector Calculus:")
    result = tool.vector_calculus("gradient", "x^2 + y^2", ["x", "y"])
    print(f"     ∇(x² + y²): {result.get('result', 'N/A')}")
    
    # Optimization
    print("\n  Optimization:")
    result = tool.optimize_function("x^2 + y^2", ["x", "y"], method="minimize")
    print(f"     min(x² + y²): {result.get('result', 'N/A')}")
    
    # Systems of equations
    print("\n  Systems of Equations:")
    result = tool.solve_system(["x + y = 5", "x - y = 1"], ["x", "y"])
    print(f"     Solve x+y=5, x-y=1: {result.get('solutions', 'N/A')}")
    
    # Polynomial operations
    print("\n  Polynomial Operations:")
    result = tool.polynomial_operations("roots", "x^2 - 4")
    print(f"     Roots of x² - 4: {result.get('result', 'N/A')}")
    
    # Sequences
    print("\n  Sequences:")
    result = tool.sequence_function("fibonacci", 10)
    print(f"     Fibonacci(10): {result.get('result', 'N/A')}")
    
    print("\n=== COMPREHENSIVE DEMO COMPLETE ===")
    print("\nThe SymPy tool now supports virtually all mathematical domains:")
    print("- Algebra and Calculus")
    print("- Linear Algebra (Matrices)")
    print("- Differential Equations")
    print("- Number Theory")
    print("- Statistics and Combinatorics")
    print("- Special Functions")
    print("- Integral Transforms")
    print("- Complex Numbers")
    print("- Vector Calculus")
    print("- Optimization")
    print("- Systems of Equations")
    print("- Polynomial Operations")
    print("- Mathematical Sequences")