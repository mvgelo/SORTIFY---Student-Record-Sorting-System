def _sort_value(record, idx):
    v = record[idx]
    if idx in (2, 5):
        return int(v)
    if idx == 3:
        return float(v)
    return str(v).lower()


def bubble_sort_students(records, key_index):
    a = list(records)
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if _sort_value(a[j], key_index) > _sort_value(a[j + 1], key_index):
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def insertion_sort_students(records, key_index):
    a = list(records)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and _sort_value(a[j], key_index) > _sort_value(key, key_index):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def quick_sort_students(records, key_index):
    if len(records) <= 1:
        return list(records)
    pivot = records[len(records) // 2]
    p = _sort_value(pivot, key_index)
    left = [r for r in records if _sort_value(r, key_index) < p]
    mid = [r for r in records if _sort_value(r, key_index) == p]
    right = [r for r in records if _sort_value(r, key_index) > p]
    return quick_sort_students(left, key_index) + mid + quick_sort_students(right, key_index)


def merge_sort_students(records, key_index):
    if len(records) <= 1:
        return list(records)
    mid = len(records) // 2
    left = merge_sort_students(records[:mid], key_index)
    right = merge_sort_students(records[mid:], key_index)

    out = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if _sort_value(left[i], key_index) <= _sort_value(right[j], key_index):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out