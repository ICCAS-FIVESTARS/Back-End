# htp_interpreter.py
# A Study on the Formal Analysis of House-Tree-Person(HTP) Test Based on AI Obejct Detection Model
"""
HTP 해석 알고리즘 구현 (위치 해석 + 크기 해석)
- 위치값: left, right, up, down, center
- 크기값: 비율(float)
"""

def analyze_position(position_dict):
    """ 객체들의 위치값 기반 해석 - htp 기반"""
    house = position_dict.get("home")
    tree = position_dict.get("tree")
    person = position_dict.get("person")
    
    result = []

    # house
    if house == 'left':
        result.append("내향적 열등감을 가지고 있다.")
    elif house == 'right':
        result.append("외향적 활동성을 가지고 있다.")

    # tree
    if tree == 'left':
        result.append("자의식이 강하고 부끄러움이 많아 내향적인 성격으로 과거로 퇴행하는 경향이 있다.")
    elif tree == 'right':
        result.append("직접만족을 강조하며 부정적 사고와 적개심을 가지는 경향이 있다.")

    # person
    if person == 'left':
        result.append("소극적이며 우울감을 가지고 있다.")
    elif person == 'right':
        result.append("이기적이며 공격적이고 분노가 높다.")

    # 공통 위치 (up/down)
    up_items = [house, tree, person].count('up')
    down_items = [house, tree, person].count('down')

    if up_items >= 2:
        result.append("동물력이 부족하고 이치에 맞지 않는 낙천주의를 가지고 있다.")
    elif down_items >= 2:
        result.append("인간감을 가지지만 우울하고 위축되어 있으며 패배감이 크다.")
    
    return result


def analyze_size(size_dict):
    """ 객체들의 크기값(비율) 기반 해석 """
    house = size_dict.get("home")
    tree = size_dict.get("tree")
    person = size_dict.get("person")
    
    result = []

    # house
    if house <= 0.33:
        result.append("열등감, 무능력감을 가지고 있고 소심하며, 자아강도가 낮다.")
    elif house > 0.67:
        result.append("과장되고 공격적이며 보상적 방어의 감정을 가지고 과잉행동을 하는 경향이 있다.")

    # person
    if person <= 0.33:
        result.append("수축된 자아를 가지고 있고 환경을 다루는데 있어서 부적절하며 낮은 에너지 수준을 가진다.")
    elif person > 0.67:
        result.append("자기를 증명하려고 노력하는 경향이 있다.")
    
    # tree
    if tree <= 0.33:
        result.append("자신에 대해 열등감을 가지고 있고 무력감을 느끼고 있다.")
    elif 0.33 < tree < 0.9:
        result.append("자기확대의 욕구를 가지며 공상보다는 현실적인 활동에서 만족을 얻으려 한다.")
    else:
        result.append("통찰력이 부족하고 생활공간으로부터의 일탈과 회의를 느낀다.")
    
    return result


def run_full_interpretation(position_dict, size_dict):
    """ 위치 + 크기 통합 해석 """
    result = []
    result += analyze_position(position_dict)
    result += analyze_size(size_dict)
    return result
