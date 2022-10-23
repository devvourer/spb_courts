from .models import Jurisdiction, Court

def get_digits(string: str) -> str:
    digits =  ''.join([i for i in string if i.isdigit()])
    return digits

def jurisdiction(court, street, parity, start=None, end=None, house_number=None):
    try:
        if not house_number:
            jurisdiction = Jurisdiction.objects.get(court=court,
                                                    street=street,
                                                    start_house_number=start,
                                                    end_house_number=end,
                                                    parity=parity
                                                    )
        else:
            jurisdiction = Jurisdiction.objects.get(court=court,
                                                    street=street,
                                                    house_number=house_number,
                                                    parity=parity)

        return jurisdiction
    except Jurisdiction.DoesNotExist:
        if not house_number:
            return Jurisdiction(court=court,
                                street=street,
                                start_house_number=start,
                                end_house_number=end,
                                parity=parity
                                )
        else:
            return Jurisdiction(court=court,
                                street=street,
                                house_number=house_number,
                                parity=parity)


# todo: Очень подумать над реализацией еще раз
def get_range(data: str, court: Court, street):
    # нечетные: все
    # нечетные: 17 - 39 (от ул. Долгоозерная до Шуваловского пр.)
    # нечетные: с 13 до конца
    # нечетные: 1, 3, 5, 7, 23, 25
    # нечетные: 1,  23 - 25
    # нечетные: 17 - 39
    # нечетные: 1-13, с 17 до конца
    # нечетные: 29,35,39,43,47-51,63-79, 91, 93, 109, 113, 123, 125-129, 133-141, 145-151

    # нечетные: все
    if data.startswith('нечетные') and data.endswith('все'):
        if not Jurisdiction.objects.filter(court=court, street=street, parity='0').exists():
            start = '1'
            end = '2000'
            parity = '0'

            return jurisdiction(court, street, parity, start, end)

    # нечетные: 17 - 39 (от ул. Долгоозерная до Шуваловского пр.)
    if data.startswith('нечетные') and data.endswith(')'):
        if not ',' in data:
            interval = data.replace('нечетные:', '').split(' (')[0].split(' - ')
            start = interval[0]
            end = interval[1]
            parity = '-1'
            
            return jurisdiction(court, street, parity, start, end)

    # нечетные: с 13 до конца
    if data.startswith('нечетные') and data.endswith('конца') and not '-' in data:
        start = get_digits(data)
        end = '2000'
        parity = '-1'
        
        return jurisdiction(court, street, parity, start, end)

    # нечетные: 1-13, с 17 до конца
    if data.startswith('нечетные') and data.endswith('конца') and '-' in data and ',' in data:
        string = data.replace('нечетные: ', '').split(',')
        parity = '-1'
        for i in string:
            if '-' in i:
                interval = i.split('-')
                start = get_digits(interval[0])
                end = get_digits(interval[1])
                return jurisdiction(court, street, parity, start=start, end=end)

            house = get_digits(i)
            return jurisdiction(court, street, parity, house_number=house)

    # нечетные: 1, 3, 5, 7, 23, 25
    if data.startswith('нечетные') and ',' in data and not '-' in data:
        parity = '-1'

        houses = data.split(': ')[1].split(',')
        for house in houses:
            return jurisdiction(court, street, parity, house_number=get_digits(house))
    
    # нечетные: 1,  23 - 25
    if data.startswith('нечетные'):
        parity = '-1'
        string = data.replace('нечетные: ', '')
        if ',' in string and '-' in string:
            houses = string.split(',')

            for house in houses:
                if '-' in house:
                    interval = house.split('-')
                    start = get_digits(interval[0])
                    end = get_digits(interval[1])
                    return jurisdiction(court, street, parity, start=start, end=end)
                
                return jurisdiction(court, street, parity, house_number=get_digits(house))

    if data.startswith('нечетные') and '-' in data:
        parity = '-1'
        interval = data.replace('нечетные:', '').split('-')
        start = get_digits(interval[0])
        end = get_digits(interval[1])

        return jurisdiction(court, street, parity, start=start, end=end)
    
    







    # четные: 17 - 39 (от ул. Долгоозерная до Шуваловского пр.)
    if data.startswith('четные') and data.endswith(')'):
        if not ',' in data:
            interval = data.replace('четные:', '').split(' (')[0].split(' - ')
            start = interval[0]
            end = interval[1]
            parity = '1'

            return jurisdiction(court, street, parity, start, end)

    # четные: с 13 до конца
    if data.startswith('четные') and data.endswith('конца') and not '-' in data:
        start = get_digits(data)
        end = '2000'
        parity = '1'
        
        return jurisdiction(court, street, parity, start, end)

    # четные: 1-13, с 17 до конца
    if data.startswith('четные') and data.endswith('конца') and '-' in data and ',' in data:
        string = data.replace('четные: ', '').split(',')
        parity = '1'
        for i in string:
            if '-' in i:
                interval = i.split('-')
                start = get_digits(interval[0])
                end = get_digits(interval[1])
                return jurisdiction(court, street, parity, start=start, end=end)
                
            house = get_digits(i)
            return jurisdiction(court, street, parity, house_number=house)

    # нечетные: 1, 3, 5, 7, 23, 25
    if data.startswith('четные') and ',' in data and not '-' in data:
        parity = '1'

        houses = data.split(': ')[1].split(',')
        for house in houses:
            return jurisdiction(court, street, parity, house_number=get_digits(house))
    
    # нечетные: 1,  23 - 25
    if data.startswith('четные'):
        parity = '1'
        string = data.replace('четные: ', '')
        if ',' in string and '-' in string:
            houses = string.split(',')

            for house in houses:
                if '-' in house:
                    interval = house.split('-')
                    start = get_digits(interval[0])
                    end = get_digits(interval[1])
                    return jurisdiction(court, street, parity, start=start, end=end)
                
                return jurisdiction(court, street, parity, house_number=get_digits(house))

    if data.startswith('четные') and '-' in data:
        parity = '1'
        interval = data.replace('нечетные:', '').split('-')
        start = get_digits(interval[0])
        end = get_digits(interval[1])

        return jurisdiction(court, street, parity, start=start, end=end)