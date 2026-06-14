
num1 = (input("Enter first number:"))
operator1 = input("Enter operator (+, -, *, /):")
num2 = (input("Enter second number;"))
if operator1 == "+":
    value = float(num1) + float(num2)
elif operator1 == "-":
    value = float(num1) - float(num2)
elif operator1 == "*":
    value = float(num1) * float(num2)
elif operator1 == "/":
    value = float(num1) / float(num2)
else:
    value = "Please enter a valid operator (No additional spaces)"

print(f"The answer is {value}")
