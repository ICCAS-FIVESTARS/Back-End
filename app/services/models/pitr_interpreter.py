def interpret_pitr(detections: list):
    result = []
    for det in detections:
        cls, bbox = det["class"], det["box"]
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        area_ratio = ((bbox[2]-bbox[0]) * (bbox[3]-bbox[1])) / (842 * 595)

        horiz = "left" if cx < 842/3 else "right" if cx > 842*2/3 else "center"
        vert = "up" if cy < 595/3 else "down" if cy > 595*2/3 else "center"

        if cls == "person":
            if horiz == "left":
                result.append("소극적이며 우울감을 가지고 있음.")
            elif horiz == "right":
                result.append("이기적이며 공격적이고 분노가 높음.")
            if vert == "up":
                result.append("통찰력이 부족하고 현실과 동떨어진 낙천주의를 가짐.")
            elif vert == "down":
                result.append("인간관계는 있으나 우울하고 위축됨.")
            if area_ratio <= 0.33:
                result.append("수축된 자아와 낮은 자존감을 가짐.")
            elif area_ratio >= 0.67:
                result.append("자기를 증명하려는 경향이 있음.")

        elif cls == "rain":
            result.append("비 요소가 포함되어 외부 자극에 대한 반응을 의미할 수 있음.")
        elif cls == "umbrella":
            result.append("방어기제를 나타내는 우산이 포함됨.")

    return {"analysis": result}