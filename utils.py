def classify(volume):
    if volume < 2000:
        return "Low"
    elif volume < 4000:
        return "Medium"
    else:
        return "High"