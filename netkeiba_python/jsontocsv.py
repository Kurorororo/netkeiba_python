import csv
import json
import re


HEADER = [# race information
          'race_id',
          'year',
          'month',
          'day',
          'is_turf',
          'is_dart',
          'is_obstacle',
          'is_right',
          'is_left',
          'distace',
          'is_sunny',
          'is_cloudy',
          'is_rainy',
          'ground_wettness',
          # horse str information
          'name',
          'jocky',
          'trainer',
          'owner',
          # horse information
          'frame',
          'number',
          'is_male',
          'is_female',
          'is_castrated',
          'age',
          'weight',
          'horse-weight',
          'horse-weight-difference',
          # odds information,
          'odds',
          'popularity',
          # horse premium information
          'time-metric',
          'train-time',
          'comments',
          'remarks',
          # result information
          'order',
          'time',
          'difference',
          'passed',
          'last-spurt',
          'prise']


def float_or_none(value):
    if value:
        return float(value)

    return None


def int_or_none(value):
    if value:
        return int(value)

    return None


def parse_title(title):
    m = re.search(r"([0-9]{4})年([0-9]{2})月([0-9]{2})日", title)

    if m:
        return m.group(1), m.group(2), m.group(3)

    return None


def parse_field(smalltxt):
    field = smalltxt[0]
    turf = 0
    dart = 0
    obstacle = 0

    if field == '芝':
        turf = 1

    if field == 'ダ':
        dart = 1

    if field == '障':
        obstacle = 1

    return turf, dart, obstacle


def parse_rotation(smalltxt):
    rotation = smalltxt[1]
    right = 0
    left = 0

    if rotation == '右':
        right = 1

    if rotation == '左':
        left = 1

    return right, left


def parse_distance(smalltxt):
    distance = None
    m = re.search(r"([0-9]+)m", smalltxt)

    if m:
        distance = int(m.group(1))

    return distance


def parse_weather(smalltxt):
    sunny = 0
    cloudy = 0
    rainy = 0
    m = re.search(r"天候 : (.)", smalltxt)
    weather = None

    if m:
        weather = m.group(1)

    if weather == '晴':
        sunny = 1

    if weather == '曇':
        cloudy = 1

    if weather == '雨':
        rainy = 1

    return sunny, cloudy, rainy


def parse_wettness(smalltxt, is_turf):
    m = None

    if is_turf:
        m = re.search(r"芝 : (.{1,2})", smalltxt)
    else:
        m = re.search(r"ダート : (.{1,2})", smalltxt)

    if not m:
        return None

    wettness_str = m.group(1)
    wettness = None

    if wettness_str[0] == '良':
        wettness = 1

    if wettness_str == '稍重':
        wettness = 2

    if wettness_str[0] == '重':
        wettness = 3

    if wettness_str == '不良':
        wettness = 4

    return wettness


def parse_age(age):
    sex = age[0]
    male = 0
    female = 0
    castrated = 0

    if sex == '牡':
        male = 1

    if sex == '牝':
        female = 1

    if sex == 'セ':
        castrated = 1

    years_old = int_or_none(age[1:])

    return male, female, castrated, years_old


def parse_odds(odds):
    if odds == '---':
        return None

    return float_or_none(odds)


def parse_horse_weight(horse_weight):
    m = re.search(r"([0-9]+)\(([+/-]?[0-9]+)\)", horse_weight)
    horse_weight_value = None
    horse_weight_difference = None

    if m:
        horse_weight_value = float(m.group(1))
        horse_weight_difference = float(m.group(2))

    return horse_weight_value, horse_weight_difference


def parse_order(order):
    if order == '取' or order == '中' or order == '除':
        return None

    m = re.match(r"([0-9]+)", order)

    if not m:
        return None

    return int_or_none(m.group(1))


def parse_time(time):
    if not time:
        return None

    m = re.search(r"([0-9]+):([0-9.]+)", time)

    if not m:
        return None

    return 60.0 * float(m.group(1)) + float(m.group(2))


def parse_prise(prise):
    if not prise:
        return None

    return float_or_none(prise.replace(',', ''))


def parse_race(race_id, race):
    print(race['title'])
    year, month, day = parse_title(race['title'])

    smalltxt = race['diary']
    turf, dart, obstacle = parse_field(smalltxt)
    right, left = parse_rotation(smalltxt)
    distance = parse_distance(smalltxt)
    sunny, cloudy, rainy = parse_weather(smalltxt)
    wettness = parse_wettness(smalltxt, turf == 1)

    return [race_id,
            year,
            month,
            day,
            turf,
            dart,
            obstacle,
            right,
            left,
            distance,
            sunny,
            cloudy,
            rainy,
            wettness]


def parse_horse(horse):
    name = horse['name']
    jocky = horse['jocky']
    trainer = horse['trainer']
    owner = horse['owner']

    frame = int_or_none(horse['frame'])
    number = int_or_none(horse['number'])
    male, female, castrated, years_old = parse_age(horse['age'])
    weight = float_or_none(horse['weight'])
    value, weight_difference = parse_horse_weight(
            horse['horse-weight'])

    odds = parse_odds(horse['odds'])
    popularity = int_or_none(horse['popularity'])

    time_metric = horse['time-metric']
    train_time = horse['train-time']
    comments = horse['comments']
    remarks = horse['remarks']

    order = parse_order(horse['order'])
    time = parse_time(horse['time'])
    difference =   horse['difference']
    passed = horse['passed']
    last_spurt = float_or_none(horse['last-spurt'])
    prise = parse_prise(horse['prise'])

    return [name,
            jocky,
            trainer,
            owner,
            frame,
            number,
            male,
            female,
            castrated,
            years_old,
            weight,
            value,
            weight_difference,
            odds,
            popularity,
            time_metric,
            train_time,
            comments,
            remarks,
            order,
            time,
            difference,
            passed,
            last_spurt,
            prise]


def main():
    with open('keiba-10y.json') as f:
        data = json.load(f)

    with open('keyba-10y.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(HEADER)

        for i, race in enumerate(data):
            race_info = parse_race(i, race)

            for horse in race['horses']:
                horse_info = parse_horse(horse)

                row = race_info + horse_info
                #print(row)
                writer.writerow(row)


if __name__ == '__main__':
    main()
