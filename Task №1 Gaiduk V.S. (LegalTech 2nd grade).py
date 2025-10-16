def fib(n):

    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Пример 1
print("Пример 1: Первые 10 чисел последовательности")
print("-" * 50)
for number in fib(10):
    print(number)

print("\n")

# Пример 2
print("Пример 2: Список первых 15 чисел")
print("-" * 50)
fibonacci_list = list(fib(15))
print(fibonacci_list)

print("\n")

# Пример 3
print("Пример 3: Первые 20 чисел в одной строке")
print("-" * 50)
result = ", ".join(str(num) for num in fib(20))
print(result)

print("\n")
