def sum_ingredients(all_ingredients):
    ingredients_sum = {}
    for name, amount, measurement_unit in all_ingredients:
        if name in ingredients_sum:
            ingredients_sum[name][0] += amount
        else:
            ingredients_sum[name] = [amount, measurement_unit]
    return ingredients_sum


def convert_ingredients_to_lines(ingredients_sum):
    lines = ['А вот и ваш список покупок:\n']
    lines += [
        f'{name} - {amount} {measurement_unit}\n'
        for name, [amount, measurement_unit] in ingredients_sum.items()
    ]
    lines.append('\n')
    lines.append('Спасибо за использование сервиса FoodGram!\n')
    lines.append('Бэкенд проекта выполнил Никита Сологуб\n')
    lines.append('Репозиторий на github: '
                 'https://github.com/dthursdays/foodgram-project-react')
    return lines
