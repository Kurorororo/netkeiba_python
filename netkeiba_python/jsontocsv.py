import argparse
import csv
import json
import re


HEADER = [# race information
          'race_id',
          'date',
          'year',
          'month',
          'day',
          'is_Jan',
          'is_Feb',
          'is_Mar',
          'is_Apr',
          'is_May',
          'is_Jun',
          'is_Jul',
          'is_Aug',
          'is_Sep',
          'is_Oct',
          'is_Nov',
          'is_Dec',
          'is_g1',
          'is_g2',
          'is_g3',
          'is_turf',
          'is_dirt',
          'is_obstacle',
          'is_right',
          'is_left',
          'is_straight',
          'distance',
          'is_sunny',
          'is_cloudy',
          'is_rainy',
          'is_turf_good',
          'is_turf_slightly_heavy',
          'is_turf_heavy',
          'is_turf_bad',
          'is_dirt_good',
          'is_dirt_slightly_heavy',
          'is_dirt_heavy',
          'is_dirt_bad',
          'number_of_horses',
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
          'horse_weight',
          'horse_weight_difference',
          # odds information,
          'odds',
          'popularity',
          # horse premium information
          'time_metric',
          'train_time',
          'comments',
          'remarks',
          # result information
          'order',
          'time',
          'difference',
          'passed',
          'last_spurt',
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
        year = m.group(1)
        month = m.group(2)
        day = m.group(3)
        date = year + '-' + month + '-' +  day

        return date, int(m.group(1)), int(m.group(2)), int(m.group(3))

    return None, None, None, None


def parse_class(title):
    g1 = 0
    g2 = 0
    g3 = 0

    if re.search(r"G1", title):
        g1 = 1

    if re.search(r"G2", title):
        g2 = 1

    if re.search(r"G3", title):
        g3 = 1

    return g1, g2, g3


def parse_field(diary):
    turf = 0
    dirt = 0
    obstacle = 0

    if re.search(r"芝", diary):
        turf = 1

    if re.search(r"ダート", diary):
        dirt = 1

    if re.search(r"障害", diary):
        obstacle = 1

    return turf, dirt, obstacle


def parse_rotation(diary):
    right = 0
    left = 0
    straight = 0

    if re.search(r"右", diary):
        right = 1

    if re.search(r"左", diary):
        left = 1

    if re.search(r"直線", diary):
        straight = 1

    return right, left, straight


def parse_distance(diary):
    distance = None
    m = re.search(r"([0-9]+)m", diary)

    if m:
        distance = int(m.group(1))

    return distance


def parse_weather(diary):
    sunny = 0
    cloudy = 0
    rainy = 0
    m = re.search(r"天候 : (.)", diary)
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


def parse_turf_wetness(diary):
    good = 0
    slightly_heavy = 0
    heavy = 0
    bad = 0

    if re.search(r"芝 : 良", diary):
        good = 1

    if re.search(r"芝 : 稍重", diary):
        slightly_heavy = 1

    if re.search(r"芝 : 重", diary):
        heavy = 1

    if re.search(r"芝 : 不良", diary):
        bad = 1

    return good, slightly_heavy, heavy, bad


def parse_dirt_wetness(diary):
    good = 0
    slightly_heavy = 0
    heavy = 0
    bad = 0

    if re.search(r"ダート : 良", diary):
        good = 1

    if re.search(r"ダート : 稍重", diary):
        slightly_heavy = 1

    if re.search(r"ダート : 重", diary):
        heavy = 1

    if re.search(r"ダート : 不良", diary):
        bad = 1

    return good, slightly_heavy, heavy, bad


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
    title = race['title']
    date, year, month, day = parse_title(title)
    race_info = [race_id, date, year, month, day]
    race_info += [1 if (i + 1) == month else 0 for i in range(12)]

    g1, g2, g3 = parse_class(title)

    diary = race['diary']
    turf, dirt, obstacle = parse_field(diary)
    right, left, straight = parse_rotation(diary)
    distance = parse_distance(diary)
    sunny, cloudy, rainy = parse_weather(diary)
    t_good, t_slightly_heavy, t_heavy, t_bad = parse_turf_wetness(diary)
    d_good, d_slightly_heavy, d_heavy, d_bad = parse_dirt_wetness(diary)
    number_of_horses = len(race['horses'])

    race_info += [g1,
                  g2,
                  g3,
                  turf,
                  dirt,
                  obstacle,
                  right,
                  left,
                  straight,
                  distance,
                  sunny,
                  cloudy,
                  rainy,
                  t_good,
                  t_slightly_heavy,
                  t_heavy,
                  t_bad,
                  d_good,
                  d_slightly_heavy,
                  d_heavy,
                  d_bad,
                  number_of_horses]

    return race_info


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


def main(infile, outfile):
    with open(infile) as f:
        data = json.load(f)

    with open(outfile, 'w') as f:
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',
                        '--infile',
                        help='入力となる JSON ファイル',
                        type=str,
                        required=True)
    parser.add_argument('-o',
                        '--outfile',
                        help='出力となる CSV ファイル',
                        type=str,
                        required=True)
    args = parser.parse_args()

    main(args.infile, args.outfile)
