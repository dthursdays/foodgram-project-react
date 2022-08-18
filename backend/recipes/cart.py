def normalize(all_ings):
    new_dict = {}
    for el in all_ings:
        if el[0] in new_dict:
            new_dict[el[0]][0] += el[1]
        else:
            new_dict[el[0]] = [el[1], el[2]]
    lines = ['А вот и ваш список покупок:\n']
    lines += [f'{k} - {v[0]} {v[1]}\n' for k, v in new_dict.items()]
    lines.append('\n')
    lines.append('Спасибо за использование сервиса FoodGram!\n')
    lines.append('Бэкенд проекта выполнил Никита Сологуб\n')
    lines.append('Репозиторий на github: '
                 'https://github.com/dthursdays/foodgram-project-react')
    return lines
