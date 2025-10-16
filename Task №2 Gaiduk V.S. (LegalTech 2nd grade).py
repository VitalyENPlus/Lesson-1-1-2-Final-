def roman_to_decimal(s):

    roman_values = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }

    s = s.upper()

    result = 0
    prev_value = 0

    for char in reversed(s):
        current_value = roman_values.get(char, 0)

        # Если текущее значение меньше предыдущего,
        # значит это вычитание (например, IV, IX, XL и т.д.)
        if current_value < prev_value:
            result -= current_value
        else:
            result += current_value

        prev_value = current_value

    return result


# Тестим
if __name__ == "__main__":
    # Примеры
    print(f'roman_to_decimal("III") = {roman_to_decimal("III")}')
    # Итог: 3

    print(f'roman_to_decimal("LVIII") = {roman_to_decimal("LVIII")}')
    # Итог: 58

    print(f'roman_to_decimal("MCMXCIV") = {roman_to_decimal("MCMXCIV")}')
    # Итог: 1994

    # Доп.
    print(f'\nДополнительные тесты:')
    print(f'roman_to_decimal("IV") = {roman_to_decimal("IV")}')
    # Итог: 4

    print(f'roman_to_decimal("IX") = {roman_to_decimal("IX")}')
    # Итог: 9

    print(f'roman_to_decimal("XL") = {roman_to_decimal("XL")}')
    # Итог: 40

    print(f'roman_to_decimal("XC") = {roman_to_decimal("XC")}')
    # Итог: 90

    print(f'roman_to_decimal("CD") = {roman_to_decimal("CD")}')
    # Итог: 400

    print(f'roman_to_decimal("CM") = {roman_to_decimal("CM")}')
    # Итог: 900

    print(f'roman_to_decimal("MMXXIII") = {roman_to_decimal("MMXXIII")}')
    # Итог: 2023