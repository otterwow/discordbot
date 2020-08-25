import random


def roll_dice(message):
    try:
        input_values = message.split()
        dice_type = max(int(input_values[0]), 1)
        num_dice = max(int(input_values[1]) if len(input_values) > 1 else 1, 1)
        if dice_type * num_dice > 9999999 or num_dice > 100:
            return "jeetje wat een hoop gedobbel zo"
        dice_values = [random.randint(1, dice_type) for i in range(num_dice)]
        if num_dice == 1:
            composition = str(dice_values[0])
        else:
            composition = f"{' + '.join([str(v) for v in dice_values])} = {sum(dice_values)}"
        return composition
    except:
        return f"{message} could not be parsed"
